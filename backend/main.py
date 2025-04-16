from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import xgboost as xgb
import pandas as pd
import numpy as np
import math
from typing import Literal          
from pathlib import Path
import json

app = FastAPI(title="XGBoost AI Calculator", description="A simple API for the XGBoost AI Calculator")

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
model_path = Path(__file__).parent / "XGBoost_model_full.json"
if not model_path.exists():
    raise FileNotFoundError(f"Model file not found at {model_path}")
model = xgb.Booster()
model.load_model(str(model_path))

class PatientData(BaseModel):
    ID: str
    DOS: str
    age: int = Field(ge=21, le=120, description="Age must be between 21 and 120 years")
    eye: Literal["OD", "OS"]
    corneal_astigmatism: float = Field(ge=0.2, le=1.50, description="Corneal Astigmatism must be between 0.20 and 1.50 D")
    steep_axis: float = Field(ge=0, le=180, description="Steep Axis must be between 0° and 180°")
    mean_k: float = Field(ge=30.00, le=50.00, description="Average K must be between 30.00 and 50.00 D")
    WTW: float = Field(ge=10.0, le=15.0, description="WTW must be between 10.0 and 15.0 mm")

    model_config = {
        "json_schema_extra": {
            "example": {
                "ID": "12345",
                "DOS": "2024-02-20",
                "age": 65,
                "eye": "OD",
                "corneal_astigmatism": 1.25,
                "steep_axis": 90,
                "mean_k": 44.00,
                "WTW": 12.0
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
        if data.corneal_astigmatism <= 0.2:
            type = "none"
        elif data.steep_axis > 140 or data.steep_axis < 40:
            type = "single"
        else:
            type = "paired"
            
        steep_axis_term = np.cos(np.radians(data.steep_axis *2))

        # Create DataFrame and predict
        df = pd.DataFrame({
            'Age': [data.age],
            'Steep_axis_term': [steep_axis_term],
            'Eye': pd.Categorical([data.eye]), 
            'WTW_IOLMaster': [data.WTW],
            'MeanK_IOLMaster': [data.mean_k],
            'Treated_astig': [data.corneal_astigmatism],
            'Residual_astigmatism': [0],
            'Type': pd.Categorical([type]), # Ensure 'none' is handled if necessary by the model or downstream processing
        })

        # Prediction may not be meaningful if type is 'none', handle accordingly
        if type != "none":
            dmatrix = xgb.DMatrix(data=df, enable_categorical=True)
            prediction = np.max(np.round(model.predict(dmatrix)), 0)
        else:
            prediction = 0 # Or handle as appropriate, e.g., skip prediction

        # Calculate arcuate positions - only if type is not 'none'
        if type != "none":
            if data.eye == "OD" and data.steep_axis > 140:
                arc1axis = data.steep_axis + 180
                arc2axis = data.steep_axis
            elif data.eye == "OS" and data.steep_axis < 40:
                arc1axis = data.steep_axis + 180
                arc2axis = data.steep_axis
            else:
                arc1axis = data.steep_axis
                arc2axis = data.steep_axis + 180
        else:
             arc1axis = 0 # Default values if no incision needed
             arc2axis = 0


        # Generate output based on type
        if type == "none":
            arc1start = arc1end = 0
            arc2start = arc2end = 0
            arcuate1text = "No arcuate incision needed"
            arcuate2text = ""
        elif type == "single":
            arc1start, arc1end = arcuatestartend(prediction, arc1axis)
            arc2start = arc2end = 0
            arc1axis = 0 if arc1axis == 360 else arc1axis # Adjust axis if it wraps around
            arcuate1text = f"Arcuate 1: {prediction:.0f} degree sweep @ {arc1axis:.0f}°"
            arcuate2text = ""
        else: # type == "paired"
            arc1start, arc1end = arcuatestartend(prediction, arc1axis)
            arc2start, arc2end = arcuatestartend(prediction, arc2axis)
            arcuate1text = f"Arcuate 1: {prediction:.0f} degree sweep @ {arc1axis:.0f}°"
            arcuate2text = f"Arcuate 2: {prediction:.0f} degree sweep @ {arc2axis:.0f}°"

        return {
            'arcuate1text': arcuate1text,
            'arcuate2text': arcuate2text,
            'arc1start': float(arc1start),
            'arc1end': float(arc1end),
            'arc2start': float(arc2start),
            'arc2end': float(arc2end)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 