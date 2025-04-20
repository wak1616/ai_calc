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
import torch
import joblib

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
model_path = Path(__file__).parent / "XGBoost_model_full.json"
if not model_path.exists():
    raise FileNotFoundError(f"Model file not found at {model_path}")
xgb_model = xgb.Booster()
xgb_model.load_model(str(model_path))

# Define the PyTorch model class
class SimpleMonotonicNN(torch.nn.Module):
    def __init__(self, other_input_dim):
        super().__init__()
        self.unconstrained_path = torch.nn.Sequential(
            torch.nn.Linear(other_input_dim, 48),
            torch.nn.LeakyReLU(0.1),
            torch.nn.Linear(48, 10),
            torch.nn.ReLU()
        )
        
    def forward(self, x_other, x_monotonic):
        coefficients = self.unconstrained_path(x_other)
        monotonic_feature_contributions = coefficients * x_monotonic
        return monotonic_feature_contributions.sum(dim=1, keepdim=True)

# Define the PyTorch prediction function
def predict_arcuate_sweep_pytorch(age, steep_axis_term, eye, wtw_iolmaster,
                         meank_iolmaster: float,
                         # Removed _one versions, kept base names
                         treatment_astigmatism,
                         type,
                         treated_astig,
                         # Paths
                         weights_path: Path,
                         components_path: Path) -> float:
    """Predicts the arcuate sweep based on input features using PyTorch model.

    Args:
        age (int): Age of the patient.
        steep_axis_term (float): Cosine of the patient's steep axis.
        eye (Literal["OD", "OS"]): Eye of the patient.
        wtw_iolmaster (float): WTW value of the patient.
        meank_iolmaster (float): The mean K value.
        treatment_astigmatism (float): Corneal astigmatism of the patient.
        type (Literal["none", "paired", "single"]): Type of arcuate incision.
        treated_astig (float): Treated corneal astigmatism of the patient.
        weights_path (Path): Path to the model weights file (.pth).
        components_path (Path): Path to the model components file (.joblib).

    Returns:
        float: Predicted arcuate sweep value (non-negative).
    """
    
    # Load model weights safely
    if not weights_path.exists():
        raise FileNotFoundError(f"PyTorch weights file not found at {weights_path}")
    if not components_path.exists():
        raise FileNotFoundError(f"PyTorch components file not found at {components_path}")

    # Load model state dict first to potentially catch file errors earlier
    try:
        model_state_dict = torch.load(weights_path, map_location=torch.device('cpu'), weights_only=True)
    except Exception as e:
        raise IOError(f"Error loading PyTorch weights from {weights_path}: {e}")

    # Load other components
    try:
        components = joblib.load(components_path)
    except Exception as e:
        raise IOError(f"Error loading components from {components_path}: {e}")
        
    # Extract components safely
    try:
        other_scaler = components['other_scaler']
        monotonic_scaler = components['monotonic_scaler']
        target_scaler = components['target_scaler']
        eye_le = components['eye_label_encoder'] 
        type_le = components['type_label_encoder'] 
        other_features_order = components['other_features_order'] # Load feature order
        monotonic_feature_order = components['monotonic_feature_order'] # Load feature order
    except KeyError as e:
        raise ValueError(f"Missing component in {components_path}: {e}")

    # Create DataFrame with raw input columns needed for both 'other' and 'monotonic' features
    # Ensure keys match the expected 'other_features' from training AND the 'treated_astig' used for monotonic input
    input_data = pd.DataFrame({
        'Age': [age],
        'Steep_axis_term': [steep_axis_term],
        'Eye': [eye],
        'WTW_IOLMaster': [wtw_iolmaster],
        'MeanK_IOLMaster': [meank_iolmaster],
        'Treatment_astigmatism': [treatment_astigmatism], # Used in other_features
        'Type': [type],
        # 'Treated_astig' column is implicitly used via the treated_astig argument below
    })

    # Prepare 'other_data' based on the loaded feature order
    # Ensure all required columns are present in input_data before selection
    missing_other_cols = [col for col in other_features_order if col not in input_data.columns]
    if missing_other_cols:
        raise ValueError(f"Missing required columns for 'other_features': {missing_other_cols}")
        
    other_data = input_data[other_features_order].copy() 

    # Apply label encoders
    try:
        # Use the fitted label encoders loaded from the file
        other_data['Eye'] = eye_le.transform(other_data['Eye'])
        other_data['Type'] = type_le.transform(other_data['Type'])
    except ValueError as e:
        # Provide more context in case of encoding errors
        problem_col = 'Eye' if 'Eye' in str(e) else 'Type'
        le_classes = eye_le.classes_ if problem_col == 'Eye' else type_le.classes_
        raise ValueError(f"Error transforming categorical feature '{problem_col}'. Input value not recognized. Ensure it's one of {list(le_classes)}. Original error: {e}")
    except Exception as e: # Catch other potential transformation errors
        raise RuntimeError(f"Error during label encoding: {e}")

    # Scale the 'other' features using the loaded scaler and order
    try:
        other_scaled = pd.DataFrame(
            other_scaler.transform(other_data),
            columns=other_features_order, 
            index=other_data.index
        )
    except Exception as e:
        raise RuntimeError(f"Error scaling 'other' features: {e}")

    # --- Monotonic Features ---
    # Use the 'treated_astig' argument directly as the input for monotonic calculations
    x_monotonic_input = treated_astig 
    log_input = x_monotonic_input + 1e-9 # Safe log input

    # Create monotonic features dictionary - ensure keys match training
    monotonic_features_dict = {
        'constant': 1.0,
        'linear': x_monotonic_input,
        'logistic_shift_left_1': 1 / (1 + np.exp(-(x_monotonic_input+1))),      
        'logistic_shift_left_0.5': 1 / (1 + np.exp(-(x_monotonic_input+0.5))),  
        'logistic_center': 1 / (1 + np.exp(-x_monotonic_input)),                
        'logarithmic': np.log(log_input), # Use safe log input
        'logistic_shift_right_0.5': 1 / (1 + np.exp(-(x_monotonic_input-0.5))), 
        'logistic_shift_right_1': 1 / (1 + np.exp(-(x_monotonic_input-1))),     
        'logistic_shift_right_1.5': 1 / (1 + np.exp(-(x_monotonic_input-1.5))), 
        'logistic_shift_left_1.5': 1 / (1 + np.exp(-(x_monotonic_input+1.5)))   
    }
    
    # Create DataFrame using the loaded monotonic feature order
    try:
        x_monotonic = pd.DataFrame([monotonic_features_dict])[monotonic_feature_order]
    except KeyError as e:
        raise ValueError(f"Mismatch between calculated monotonic features and expected order from components file. Missing key: {e}")
    
    # Scale monotonic features using loaded scaler and order
    try:
        monotonic_scaled = pd.DataFrame(
            monotonic_scaler.transform(x_monotonic),
            columns=monotonic_feature_order,
            index=x_monotonic.index
        )
    except Exception as e:
        raise RuntimeError(f"Error scaling 'monotonic' features: {e}")
    
    # Convert to tensors
    x_other_tensor = torch.FloatTensor(other_scaled.values)
    x_monotonic_tensor = torch.FloatTensor(monotonic_scaled.values)
    
    # Initialize model and load weights
    # Ensure the input dimension matches the loaded feature order length
    model = SimpleMonotonicNN(len(other_features_order)) 
    try:
        model.load_state_dict(model_state_dict)
    except Exception as e:
        raise RuntimeError(f"Error loading state dict into model: {e}")
    model.eval()
    
    # Make prediction
    try:
        with torch.no_grad():
            prediction_scaled = model(x_other_tensor, x_monotonic_tensor)
            prediction = target_scaler.inverse_transform(prediction_scaled.numpy())
            prediction = max(0.0, float(prediction.item()))  # Ensure non-negative
            return prediction
    except Exception as e:
        raise RuntimeError(f"Error during model prediction: {e}")

class PatientData(BaseModel):
    ID: str
    DOS: str
    age: int = Field(ge=21, le=120, description="Age must be between 21 and 120 years")
    eye: Literal["OD", "OS"]
    corneal_astigmatism: float = Field(ge=0.25, le=1.50, description="Corneal Astigmatism must be between 0.25 and 1.50 D")
    steep_axis: float = Field(ge=0, le=180, description="Steep Axis must be between 0° and 180°")
    mean_k: float = Field(ge=30.00, le=50.00, description="Average K must be between 30.00 and 50.00 D")
    WTW: float = Field(ge=10.0, le=15.0, description="WTW must be between 10.0 and 15.0 mm")
    model_choice: Literal["XGBoost", "Monotonic Neural Network"]

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
                "model_choice": "XGBoost"
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
                # XGBoost prediction (remains unchanged)
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

            elif data.model_choice == "Monotonic Neural Network":
                # PyTorch Prediction
                # === Removed calculation of _one variables ===
                
                # === Use corneal_astigmatism directly based on training script simplification ===
                treatment_astigmatism_input = data.corneal_astigmatism
                treated_astig_input = data.corneal_astigmatism 
                # === End Modification ===

                # Define paths to model files (relative to main.py)
                pytorch_weights_path = Path(__file__).parent / "model_weights.pth"
                pytorch_components_path = Path(__file__).parent / "model_components.joblib"

                # === Modified: Update function call with simplified arguments ===
                prediction = predict_arcuate_sweep_pytorch(
                    age=data.age,
                    steep_axis_term=steep_axis_term,
                    eye=data.eye,
                    wtw_iolmaster=data.WTW,
                    meank_iolmaster=data.mean_k,
                    treatment_astigmatism=treatment_astigmatism_input,
                    type=type, 
                    treated_astig=treated_astig_input, 
                    # Paths
                    weights_path=pytorch_weights_path,
                    components_path=pytorch_components_path
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