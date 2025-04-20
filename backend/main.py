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
import joblib
from sklearn.linear_model import Ridge

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
model_path = Path("/data/XGBoost_model_full.json") # Load from mounted persistent disk
if not model_path.exists():
    # Fallback for local development (assuming files are in ./backend)
    local_fallback_path = Path(__file__).parent / "XGBoost_model_full.json"
    if local_fallback_path.exists():
        model_path = local_fallback_path
    else:
        raise FileNotFoundError(f"Model file not found at /data/XGBoost_model_full.json or {local_fallback_path}")
xgb_model = xgb.Booster()
xgb_model.load_model(str(model_path))

# Define the Ridge prediction function
def predict_arcuate_sweep_ridge(age, steep_axis_term, eye, wtw_iolmaster,
                         meank_iolmaster: float,
                         type,
                         treated_astig,
                         # Paths
                         model_path: Path,
                         components_path: Path) -> float:
    """Predicts the arcuate sweep based on input features using the Ridge model.

    Args:
        age (int): Age of the patient.
        steep_axis_term (float): Cosine of the patient's steep axis.
        eye (Literal["OD", "OS"]): Eye of the patient.
        wtw_iolmaster (float): WTW value of the patient.
        meank_iolmaster (float): The mean K value.
        type (Literal["none", "paired", "single"]): Type of arcuate incision.
        treated_astig (float): Treated corneal astigmatism (used for 'monotonic features').
        model_path (Path): Path to the Ridge model file (.joblib).
        components_path (Path): Path to the model components file (.joblib).

    Returns:
        float: Predicted arcuate sweep value (non-negative).
    """
    
    # Load model and components safely
    if not model_path.exists():
        raise FileNotFoundError(f"Ridge model file not found at {model_path}")
    if not components_path.exists():
        raise FileNotFoundError(f"Ridge components file not found at {components_path}")

    # Load model and components
    try:
        model = joblib.load(model_path)
        components = joblib.load(components_path)
    except Exception as e:
        raise IOError(f"Error loading model or components: {e}")
        
    # Extract components safely
    try:
        other_scaler = components['other_scaler']
        monotonic_scaler = components['monotonic_scaler']
        eye_le = components['eye_label_encoder'] 
        type_le = components['type_label_encoder'] 
        other_features_order = components['other_features_order']
        monotonic_feature_order = components['monotonic_feature_order']
    except KeyError as e:
        raise ValueError(f"Missing component in {components_path}: {e}")

    # --- Prepare Input Data --- 
    # Create DataFrame for 'other' features based on components order
    other_dict = {
        'Age': age,
        'Steep_axis_term': steep_axis_term,
        'Eye': eye,
        'WTW_IOLMaster': wtw_iolmaster,
        'MeanK_IOLMaster': meank_iolmaster,
        'Type': type
    }
    # Ensure all keys expected by other_features_order are present
    if not all(key in other_dict for key in other_features_order):
         missing_keys = set(other_features_order) - set(other_dict.keys())
         raise ValueError(f"Missing required keys for 'other_features': {missing_keys}")
         
    other_data = pd.DataFrame([other_dict])[other_features_order] # Ensure order

    # Apply label encoders (handle potential unseen values if necessary, although less likely with Literal)
    try:
        other_data['Eye'] = eye_le.transform(other_data['Eye'])
        other_data['Type'] = type_le.transform(other_data['Type'])
    except ValueError as e:
        # Handle cases where input might somehow bypass Literal validation
        problem_col = 'Eye' if 'Eye' in str(e) else 'Type'
        le_classes = eye_le.classes_ if problem_col == 'Eye' else type_le.classes_
        raise ValueError(f"Error transforming categorical feature '{problem_col}'. Input value not recognized. Ensure it's one of {list(le_classes)}. Original error: {e}")

    # Scale 'other' features
    try:
        other_scaled = pd.DataFrame(
            other_scaler.transform(other_data),
            columns=other_features_order, 
            index=other_data.index
        )
    except Exception as e:
        raise RuntimeError(f"Error scaling 'other' features: {e}")

    # --- Monotonic Features --- 
    x_monotonic_input = treated_astig
    # NOTE: x_min for log transform was implicitly handled during scaler fitting in final_ridge_model.py
    # The monotonic_scaler *learned* the appropriate scaling based on log(x - x_min + 1)
    # So we just need to apply the same transformations here before scaling.
    log_input = x_monotonic_input + 1e-9 # Add epsilon for log safety, although x_min handling should make it >= 1

    monotonic_features_dict = {
        'constant': 1.0,
        'linear': x_monotonic_input,
        'logistic_shift_left_1': 1 / (1 + np.exp(-(x_monotonic_input+1))),      
        'logistic_shift_left_0.5': 1 / (1 + np.exp(-(x_monotonic_input+0.5))),  
        'logistic_center': 1 / (1 + np.exp(-x_monotonic_input)),                
        # Use log(input + eps) directly. The scaler implicitly handles the 'x_min' shift during its fit.
        'logarithmic': np.log(log_input), 
        'logistic_shift_right_0.5': 1 / (1 + np.exp(-(x_monotonic_input-0.5))), 
        'logistic_shift_right_1': 1 / (1 + np.exp(-(x_monotonic_input-1))),     
        'logistic_shift_right_1.5': 1 / (1 + np.exp(-(x_monotonic_input-1.5))), 
        'logistic_shift_left_1.5': 1 / (1 + np.exp(-(x_monotonic_input+1.5)))   
    }
    
    try:
        x_monotonic = pd.DataFrame([monotonic_features_dict])[monotonic_feature_order]
    except KeyError as e:
        raise ValueError(f"Mismatch between calculated monotonic features and expected order from components file. Missing key: {e}")

    # Scale monotonic features
    try:
        monotonic_scaled = pd.DataFrame(
            monotonic_scaler.transform(x_monotonic),
            columns=monotonic_feature_order,
            index=x_monotonic.index
        )
    except Exception as e:
        raise RuntimeError(f"Error scaling 'monotonic' features: {e}")

    # --- Combine Features & Predict --- 
    X_combined = pd.concat([other_scaled, monotonic_scaled], axis=1)

    # Make prediction
    try:
        prediction = model.predict(X_combined)[0] # Predict returns array, get first element
        prediction = max(0.0, float(prediction))  # Ensure non-negative
        return prediction
    except Exception as e:
        raise RuntimeError(f"Error during Ridge model prediction: {e}")

class PatientData(BaseModel):
    ID: str
    DOS: str
    age: int = Field(ge=21, le=120, description="Age must be between 21 and 120 years")
    eye: Literal["OD", "OS"]
    corneal_astigmatism: float = Field(ge=0.25, le=1.50, description="Corneal Astigmatism must be between 0.25 and 1.50 D")
    steep_axis: float = Field(ge=0, le=180, description="Steep Axis must be between 0° and 180°")
    mean_k: float = Field(ge=30.00, le=50.00, description="Average K must be between 30.00 and 50.00 D")
    WTW: float = Field(ge=10.0, le=15.0, description="WTW must be between 10.0 and 15.0 mm")
    model_choice: Literal["XGBoost", "Ridge Regression"]

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
                "WTW": 12.0,
                "model_choice": "Ridge Regression"
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
            if data.model_choice == "XGBoost":
                # XGBoost prediction
                df = pd.DataFrame({
                    'Age': [data.age],
                    'Steep_axis_term': [steep_axis_term],
                    'Eye': pd.Categorical([data.eye]),
                    'WTW_IOLMaster': [data.WTW],
                    'MeanK_IOLMaster': [data.mean_k],
                    'Treated_astig': [data.corneal_astigmatism],
                    'Treatment_astigmatism': [data.corneal_astigmatism],
                    'Type': pd.Categorical([type])
                })
           
                dmatrix = xgb.DMatrix(data=df, enable_categorical=True)
                prediction = np.max(xgb_model.predict(dmatrix), 0)

            elif data.model_choice == "Ridge Regression":
                # PyTorch Prediction (SECTION REPLACED WITH RIDGE)
                # === Use corneal_astigmatism directly based on training script simplification ===
                treated_astig_input = data.corneal_astigmatism
                # === End Modification ===

                # Define paths to Ridge model files (expecting them in /data/)
                ridge_model_path = Path("/data/ridge_model.joblib")
                ridge_components_path = Path("/data/ridge_components.joblib")

                # Fallback for local development (assuming files are in ./backend)
                if not ridge_model_path.exists():
                    local_fallback_path = Path(__file__).parent / "ridge_model.joblib"
                    if local_fallback_path.exists():
                        ridge_model_path = local_fallback_path
                    else:
                        raise FileNotFoundError(f"Ridge model file not found at /data/ridge_model.joblib or {local_fallback_path}")
                if not ridge_components_path.exists():
                     local_fallback_path = Path(__file__).parent / "ridge_components.joblib"
                     if local_fallback_path.exists():
                         ridge_components_path = local_fallback_path
                     else:
                         raise FileNotFoundError(f"Ridge components file not found at /data/ridge_components.joblib or {local_fallback_path}")

                # === Modified: Call Ridge prediction function ===
                prediction = predict_arcuate_sweep_ridge(
                    age=data.age,
                    steep_axis_term=steep_axis_term,
                    eye=data.eye,
                    wtw_iolmaster=data.WTW,
                    meank_iolmaster=data.mean_k,
                    type=type,
                    treated_astig=treated_astig_input,
                    # Paths
                    model_path=ridge_model_path,
                    components_path=ridge_components_path
                )
                # === End Modified ===

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