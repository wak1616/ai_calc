# Arcuate Incision Calculator

A web application for calculating and visualizing arcuate incisions for astigmatism correction in cataract surgery.

## Features

- Patient data input validation
- AI-powered incision length prediction *(using XGBoost or Monotonic Neural Network model)*
- Visual representation of arcuate incisions
- Support for both single and paired arcuates
- Selectable prediction model (XGBoost or Monotonic Neural Network)


## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm (Node Package Manager)

## Installation

1. Clone the repository
2. Install Python dependencies:
```sh
cd backend # Navigate to backend directory first
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd .. # Go back to the root directory
```

3. Install Node.js dependencies:
```sh
npm install
```

## Development

To run the application in development mode:

1. Start the backend server:
```sh
cd backend
source venv/bin/activate # Or venv\Scripts\activate on Windows
uvicorn main:app --reload # Use uvicorn directly for development reload
cd ..
```

2. In a separate terminal, start the frontend development server:
```sh
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Production Build

To build for production:

```sh
npm run build
python run.py
```

The application will be served at http://localhost:8000

## Model Information

The application uses an XGBoost model and optionally a PyTorch-based Monotonic Neural Network model for predictions. 

- The XGBoost model file `XGBoost_model_full.json` is included in this repository in the `backend/` directory.
- **For the Monotonic Neural Network option:** You need to place the following files into the `backend/` directory:
    - `model_weights.pth` (PyTorch model state dictionary)
    - `model_components.joblib` (Scalers and label encoders)

These files are required for the "Monotonic Neural Network" selection to function.

## Dependencies

The backend requires Python packages listed in `backend/requirements.txt`, including `fastapi`, `xgboost`, `pandas`, `numpy`, `torch`, and `joblib`.

The frontend requires Node.js packages listed in `package.json`, including `vue` and `vuetify`.
