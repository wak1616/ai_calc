# Arcuate Incision Calculator

A web application for using machine learning models to calculate laser arcuate incisions for astigmatism correction in cataract surgery.

## Features

- Patient data input validation (e.g., Corneal Astigmatism: 0.25-1.50 D)
- AI-powered incision length prediction (using XGBoost or Ridge Regression model)
- Visual representation of arcuate incisions
- Support for both single and paired arcuates
- Selectable prediction model (XGBoost or Ridge Regression, XGBoost is default)


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

To build the frontend assets for production:

```sh
npm run build
```

To serve the application in a production-like environment (using the built frontend assets):

```sh
cd backend
source venv/bin/activate # Or venv\Scripts\activate on Windows
# Ensure your .env or environment variables are set for production if needed
uvicorn main:app --host 0.0.0.0 --port 8000 # Use uvicorn directly, adjust host/port as needed
cd ..
```

Note: For a true production deployment, consider using a process manager like Gunicorn or Supervisor behind a reverse proxy like Nginx.

## Model Information

The application uses an XGBoost model (default) and optionally a Scikit-learn Ridge Regression model for predictions.

The XGBoost model incorporates a comprehensive set of patient-specific data to deliver personalized arcuate incision recommendations. It analyzes critical features including:
- Corneal astigmatism
- Steep axis position
- Eye laterality (OD/OS)
- White-to-white distance (WTW)
- Average keratometry (Mean K)
- Axial length (AL)
- Patient age
- Prior LASIK history

The model has been specifically designed with a monotonic constraint on the astigmatism feature, ensuring that as corneal astigmatism increases, the recommended arcuate incision length will never decrease. This constraint ensures clinical relevance and predictability in surgical planning.

**Important:** For privacy and security, the model files (`XGBoost_smooth_model_latest.json`, `ridge_model.joblib`, `ridge_components.joblib`) are **not** included in this public repository and are listed in `.gitignore`.

To run the application locally or deploy it, you need to obtain these files and place them in the `backend/` directory:
    - `XGBoost_smooth_model_latest.json` (XGBoost model)


These files are required for the application predictions to function. For deployment (e.g., on Render), these files should be securely uploaded to the server environment (e.g., using Render Persistent Disks) rather than being committed to the repository.

## Dependencies

The backend requires Python packages listed in `backend/requirements.txt`, including `fastapi`, `xgboost`, `pandas`, `numpy`, `scikit-learn`, and `joblib`.

The frontend requires Node.js packages listed in `package.json`, including `vue` and `vuetify`.
