from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import xgboost as xgb
import pandas as pd
import numpy as np
import math
from typing import Literal          
from pathlib import Path

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Load the XGBoost model
model_path = Path(__file__).parent / "model_full_ver7.json"
if not model_path.exists():
    raise FileNotFoundError(f"Model file not found at {model_path}")
model = xgb.Booster()
model.load_model(str(model_path))

class PatientData(BaseModel):
    ID: str
    DOS: str
    age: int = Field(ge=21, le=120, description="Age must be between 21 and 120 years")
    eye: Literal["OD", "OS"]
    corneal_astigmatism: float = Field(gt=0.2, le=1.50, description="Corneal Astigmatism must be between 0.20 and 1.50 D")
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
        type = "single" if (data.steep_axis > 140 or data.steep_axis < 40) else "paired"
        steep_axis_term = np.cos(np.radians(data.steep_axis) * 2)
        corneal_astigmatism = data.corneal_astigmatism / 2 if type == "paired" else data.corneal_astigmatism
        
        # Create DataFrame and predict
        df = pd.DataFrame({
            'Age': [data.age],
            'Steep_axis_term': [steep_axis_term],
            'WTW_IOLMaster': [data.WTW],
            'MeanK_IOLMaster': [data.mean_k],
            'type': pd.Categorical([type]),
            'treated_astig': [corneal_astigmatism],
            'Residual_Astigmatism': [0]
        })
        
        dmatrix = xgb.DMatrix(data=df, enable_categorical=True)
        prediction = np.max(np.round(model.predict(dmatrix)), 0)

        # Calculate arcuate positions
        if data.eye == "OD" and data.steep_axis > 140:
            arc1axis = data.steep_axis + 180
            arc2axis = data.steep_axis
        elif data.eye == "OS" and data.steep_axis < 40:
            arc1axis = data.steep_axis + 180
            arc2axis = data.steep_axis
        else: 
            arc1axis = data.steep_axis
            arc2axis = data.steep_axis + 180

        # Generate output
        if type == "single":
            arc1start, arc1end = arcuatestartend(prediction, arc1axis)
            arc2start = arc2end = 0
            arc1axis = 0 if arc1axis == 360 else arc1axis
            arcuate1text = f"Arcuate 1: {prediction:.0f} degree sweep @ {arc1axis:.0f}°"
            arcuate2text = ""
        else:
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