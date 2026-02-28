from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import xgboost as xgb
import pandas as pd
import numpy as np
import math
from typing import Literal
from pathlib import Path
import os
import logging

logger = logging.getLogger("ai_calc.backend")


def env_flag(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


enable_api_docs = env_flag("ENABLE_API_DOCS", "true")
app = FastAPI(
    title="AI Calculator",
    description="A simple API for calculating laser arcuate incisions using machine learning algorithms",
    docs_url="/docs" if enable_api_docs else None,
    redoc_url="/redoc" if enable_api_docs else None,
    openapi_url="/openapi.json" if enable_api_docs else None,
)

max_request_size_bytes = int(os.getenv("MAX_REQUEST_SIZE_BYTES", "8192"))
set_hsts_header = env_flag("SET_HSTS_HEADER", "true")

# Generate a list of localhost origins for ports 8000-8010
localhost_origins = [f"http://localhost:{port}" for port in range(8000, 8011)]
# Also add development frontend server origins
frontend_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
# Production origins
prod_origins = [
    "https://aicalc.derojas.ai",
    "https://derojas.ai",
    "https://www.derojas.ai",
    # Keep these if still in use.
    "https://derojas.info",
    "https://www.derojas.info",
]

env_origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "").split(",") if origin.strip()]
allow_origin_regex = os.getenv("ALLOW_ORIGIN_REGEX", r"https?://(localhost:\d+|.*\.vercel\.app)")

allowed_origins = [*prod_origins, *frontend_origins, *localhost_origins, *env_origins]

# Add CORS middleware with all possible origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.middleware("http")
async def enforce_request_size_and_security_headers(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > max_request_size_bytes:
        return JSONResponse(status_code=413, content={"detail": "Request body too large"})

    if content_length is None and request.method in {"POST", "PUT", "PATCH"}:
        body = await request.body()
        if len(body) > max_request_size_bytes:
            return JSONResponse(status_code=413, content={"detail": "Request body too large"})

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    if set_hsts_header:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.get("/healthz")
@app.get("/health")
async def healthz():
    return {"status": "ok"}


# Load the XGBoost model
model_path = Path("/data/XGBoost_smooth_model_latest.json")  # Load from mounted persistent disk
if not model_path.exists():
    # Fallback for local development (assuming files are in ./backend)
    local_fallback_path = Path(__file__).parent / "XGBoost_smooth_model_latest.json"
    if local_fallback_path.exists():
        model_path = local_fallback_path
    else:
        raise FileNotFoundError(f"Model file not found at /data/XGBoost_smooth_model_latest.json or {local_fallback_path}")
xgb_model = xgb.Booster()
xgb_model.load_model(str(model_path))


class PatientData(BaseModel):
    # HIPAA: No patient-identifying fields (Name, ID, DOS) are accepted server-side.
    # Only de-identified clinical parameters needed for prediction.
    age: int = Field(ge=21, le=120, description="Age must be between 21 and 120 years")
    eye: Literal["OD", "OS"]
    corneal_astigmatism: float = Field(ge=0.25, le=1.25, description="Corneal Astigmatism must be between 0.25 and 1.50 D")
    steep_axis: float = Field(ge=0, le=180, description="Steep Axis must be between 0° and 180°")
    WTW: float = Field(ge=10.0, le=15.0, description="WTW must be between 10.0 and 15.0 mm")
    AL: float = Field(ge=20.0, le=31.0, description="Axial Length must be between 20.0 and 31.0 mm")
    LASIK: Literal["hyperopic", "myopic", "no"]

    model_config = {
        "json_schema_extra": {
            "example": {
                "age": 65,
                "eye": "OD",
                "corneal_astigmatism": 1.25,
                "steep_axis": 90,
                "WTW": 12.0,
                "AL": 24.5,
                "LASIK": "no",
            }
        }
    }


def arcuatestartend(sweep: float, location: float) -> tuple[float, float]:
    location = 360 if location == 0 else 360 - location
    arcstart_deg = (location - sweep / 2) % 360
    arcend_deg = (location + sweep / 2) % 360
    return (math.radians(arcstart_deg), math.radians(arcend_deg))


@app.post("/predict")
async def predict(data: PatientData):
    try:
        # Calculate derived variables
        if data.corneal_astigmatism < 0.25:
            incision_type = "none"
        elif 40 <= data.steep_axis <= 140:
            # Consistent with training script's 'Type' column generation if arcuate is paired
            incision_type = "paired"
        else:
            # Consistent with training script's 'Type' column generation if arcuate is single
            incision_type = "single"

        steep_axis_term = np.cos(np.radians(data.steep_axis * 2))

        # Prediction logic
        prediction = 0.0  # Default prediction
        if incision_type != "none":
            # XGBoost prediction
            xgb_df = pd.DataFrame(
                {
                    "Age": [data.age],
                    "Steep_axis_term": [steep_axis_term],
                    "WTW_IOLMaster": [data.WTW],
                    "Treated_astig": [data.corneal_astigmatism],
                    "Type": [incision_type],
                    "AL": [data.AL],
                    "LASIK?": [data.LASIK],
                }
            )

            # Convert categorical columns to category type
            categorical_columns = ["Type", "LASIK?"]
            for col in categorical_columns:
                xgb_df[col] = xgb_df[col].astype("category")

            # Create DMatrix with categorical features enabled
            dmatrix = xgb.DMatrix(xgb_df, enable_categorical=True)

            # Get prediction
            prediction = xgb_model.predict(dmatrix)[0]

            # Divide prediction by 2 if type is paired BEFORE capping
            if incision_type == "paired":
                prediction /= 2
                prediction = min(prediction, 50)
                prediction = round(prediction)
            else:
                prediction = min(prediction, 50)
                prediction = round(prediction)

        # Calculate arcuate positions - only if type is not 'none'
        # Initialize values assuming no incision
        arc1start, arc1end, arc2start, arc2end = 0.0, 0.0, 0.0, 0.0
        arc1axis, arc2axis = 0.0, 0.0
        arcuate1text = "No arcuate incision needed"
        arcuate2text = ""

        # MODIFIED: Check prediction > 0 AFTER all calculations
        if incision_type != "none" and prediction > 0:
            # Axis calculation logic remains the same
            if (data.eye == "OD" and data.steep_axis > 140) or (data.eye == "OS" and data.steep_axis < 40):
                # Single ATR case
                arc1axis = data.steep_axis + 180 if data.steep_axis < 180 else data.steep_axis - 180
                arc1axis = arc1axis % 360
                arc2axis = data.steep_axis
            else:
                # Includes paired and single WTR
                arc1axis = data.steep_axis
                arc2axis = (data.steep_axis + 180) % 360

            # Calculate start/end angles and generate text based on type
            if incision_type == "single":
                arc1start, arc1end = arcuatestartend(prediction, arc1axis)
                arc1axis_display = round(arc1axis)
                arcuate1text = f"Arcuate 1: {prediction:.0f} degree sweep @ {arc1axis_display:.0f}°"
            elif incision_type == "paired":
                arc1start, arc1end = arcuatestartend(prediction, arc1axis)
                arc2start, arc2end = arcuatestartend(prediction, arc2axis)
                arc1axis_display = round(arc1axis)
                arc2axis_display = round(arc2axis)
                arcuate1text = f"Arcuate 1: {prediction:.0f} degree sweep @ {arc1axis_display:.0f}°"
                arcuate2text = f"Arcuate 2: {prediction:.0f} degree sweep @ {arc2axis_display:.0f}°"

        return {
            "arcuate1text": arcuate1text,
            "arcuate2text": arcuate2text,
            "arc1start": arc1start,
            "arc1end": arc1end,
            "arc2start": arc2start,
            "arc2end": arc2end,
        }

    except FileNotFoundError:
        # HIPAA-safe: avoid request payload logging.
        logger.exception("Model or component file not found")
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: Required model file not found. Please contact support.",
        )
    except (ValueError, IOError, RuntimeError):
        # HIPAA-safe: avoid request payload logging.
        logger.exception("Error in prediction pipeline")
        raise HTTPException(status_code=500, detail="Error processing prediction. Please verify your inputs and try again.")
    except HTTPException:
        # Re-raise HTTPExceptions directly (e.g., from validation)
        raise
    except Exception:
        # HIPAA-safe: avoid request payload logging.
        logger.exception("Unexpected error during prediction")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again.")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
