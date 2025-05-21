from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import xgboost as xgb
import pandas as pd
import numpy as np
import math
from typing import Literal, Tuple          
from pathlib import Path
import json

app = FastAPI(title="AI Calculator", description="A simple API for calculating laser arcuate incisions using machine learning algorithms")

# Generate a list of localhost origins for ports 8000-8010
localhost_origins = [f"http://localhost:{port}" for port in range(8000, 8011)]
# Also add development frontend server origins
frontend_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
# Production origins
prod_origins = [
    "https://derojas.info", "http://derojas.info", 
    "https://www.derojas.info", "http://www.derojas.info",
    # Vercel deployment domains
    "https://*.vercel.app"
]

# Add CORS middleware with all possible origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[*prod_origins, *frontend_origins, *localhost_origins],
    allow_origin_regex=r"https?://(localhost:\d+|.*\.vercel\.app)",  # Updated regex to include vercel.app domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Load the XGBoost model
model_path = Path("/data/XGBoost_smooth_model_latest.json") # Load from mounted persistent disk
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
    ID: str
    DOS: str
    age: int = Field(ge=21, le=120, description="Age must be between 21 and 120 years")
    eye: Literal["OD", "OS"]
    corneal_astigmatism: float = Field(ge=0.25, le=1.50, description="Corneal Astigmatism must be between 0.25 and 1.50 D")
    steep_axis: float = Field(ge=0, le=180, description="Steep Axis must be between 0° and 180°")
    WTW: float = Field(ge=10.0, le=15.0, description="WTW must be between 10.0 and 15.0 mm")
    AL: float = Field(ge=20.0, le=31.0, description="Axial Length must be between 20.0 and 31.0 mm")
    LASIK: Literal["hyperopic", "myopic", "no"]

    model_config = {
        "json_schema_extra": {
            "example": {
                "ID": "12345",
                "DOS": "2024-02-20",
                "age": 65,
                "eye": "OD",
                "corneal_astigmatism": 1.25,
                "steep_axis": 90,
                "WTW": 12.0,
                "AL": 24.5,
                "LASIK": "no"
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
            type = "none"
        elif data.steep_axis >= 40 and data.steep_axis <= 140:
            # Consistent with training script's 'Type' column generation if arcuate is paired
            type = "paired"
        else:
            # Consistent with training script's 'Type' column generation if arcuate is single
            type = "single"
            
        steep_axis_term = np.cos(np.radians(data.steep_axis * 2))

        # Prediction logic
        prediction = 0.0 # Default prediction
        if type != "none":
            # XGBoost prediction
            xgb_df = pd.DataFrame({
                'Age': [data.age],
                'Steep_axis_term': [steep_axis_term],
                'WTW_IOLMaster': [data.WTW],
                'Treated_astig': [data.corneal_astigmatism],
                'Type': [type],
                'AL': [data.AL],
                'LASIK?': [data.LASIK]
            })
            
            # Convert categorical columns to category type
            categorical_columns = ['Type', 'LASIK?']
            for col in categorical_columns:
                xgb_df[col] = xgb_df[col].astype('category')
            
            # Create DMatrix with categorical features enabled
            dmatrix = xgb.DMatrix(xgb_df, enable_categorical=True)
            
            # Get prediction
            xgb_prediction = xgb_model.predict(dmatrix)[0]
            prediction = xgb_prediction
            
            # Debug logging
            print(f"XGBoost prediction input: {xgb_df.to_dict('records')[0]}")
            print(f"XGBoost prediction output: {prediction}")

            # Divide prediction by 2 if type is paired BEFORE capping
            if type == "paired":
                prediction /= 2
                prediction = min(prediction, 50) 
                prediction = round(prediction)
            else:
                prediction = min(prediction, 50) 
                prediction = round(prediction) # Round the prediction 

        else:
            # Type is "none", prediction remains 0
            pass 

        # Calculate arcuate positions - only if type is not 'none'
        # Initialize values assuming no incision
        arc1start, arc1end, arc2start, arc2end = 0.0, 0.0, 0.0, 0.0
        arc1axis, arc2axis = 0.0, 0.0
        arcuate1text = "No arcuate incision needed" # Default text
        arcuate2text = ""

        # MODIFIED: Check prediction > 0 AFTER all calculations
        if type != "none" and prediction > 0:
            # Axis calculation logic remains the same
            if (data.eye == "OD" and data.steep_axis > 140) or \
               (data.eye == "OS" and data.steep_axis < 40): # Single ATR case
                 arc1axis = data.steep_axis + 180 if data.steep_axis < 180 else data.steep_axis - 180 # Ensure stays within 0-360 logic for arcuatestartend
                 arc1axis = arc1axis % 360 # Normalize axis
                 arc2axis = data.steep_axis # For potential display, not used in calculation for single
            else: # Includes paired and single WTR
                arc1axis = data.steep_axis
                arc2axis = (data.steep_axis + 180) % 360 # Normalize paired axis

            # Calculate start/end angles and generate text based on type
            if type == "single":
                 arc1start, arc1end = arcuatestartend(prediction, arc1axis)
                 # Update text only if prediction > 0
                 arc1axis_display = round(arc1axis)
                 arcuate1text = f"Arcuate 1: {prediction:.0f} degree sweep @ {arc1axis_display:.0f}°"
                 # arc2start, arc2end, arcuate2text remain default (0 or empty)
            elif type == "paired":
                 arc1start, arc1end = arcuatestartend(prediction, arc1axis)
                 arc2start, arc2end = arcuatestartend(prediction, arc2axis)
                 # Update text only if prediction > 0
                 arc1axis_display = round(arc1axis)
                 arc2axis_display = round(arc2axis)
                 arcuate1text = f"Arcuate 1: {prediction:.0f} degree sweep @ {arc1axis_display:.0f}°"
                 arcuate2text = f"Arcuate 2: {prediction:.0f} degree sweep @ {arc2axis_display:.0f}°"

        # Ensure JSON serializability (arc angles are already floats)
        return {
            'arcuate1text': arcuate1text,
            'arcuate2text': arcuate2text,
            'arc1start': arc1start,
            'arc1end': arc1end,
            'arc2start': arc2start,
            'arc2end': arc2end
        }
    
    except FileNotFoundError as e:
         # Specific handling for model/component file issues
         print(f"ERROR: Model or component file not found: {e}")
         raise HTTPException(status_code=500, detail=f"Server configuration error: Required model file not found. Please contact support.")
    except (ValueError, IOError, RuntimeError) as e:
        # Handle errors originating from the prediction function (missing components, scaling issues, etc.)
        print(f"ERROR in prediction pipeline: {e}")
        # Avoid leaking detailed internal errors to the client
        raise HTTPException(status_code=500, detail=f"Error processing prediction: {e}") 
    except HTTPException:
        # Re-raise HTTPExceptions directly (e.g., from validation)
        raise
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Unexpected ERROR during prediction: {e}")
        import traceback
        traceback.print_exc() # Log the full traceback for debugging
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 