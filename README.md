# Arcuate Incision Calculator

A web application for calculating and visualizing arcuate incisions for astigmatism correction in cataract surgery.

## Features

- Patient data input validation
- AI-powered incision length prediction *(using XGBoost model)*
- Visual representation of arcuate incisions
- Support for both single and paired arcuates


## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm (Node Package Manager)

## Installation

1. Clone the repository
2. Install Python dependencies:
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Install Node.js dependencies:
```sh
npm install
```

## Development

To run the application in development mode:

1. Start the backend server:
```sh
python run.py
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

The application uses an XGBoost model for predictions. The model file `XGBoost-model_full.json` is included in this repository in the `backend/` directory.
