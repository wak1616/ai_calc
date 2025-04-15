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

The application uses XGBoost model version 7 for predictions. The model file `model_full_ver7.json` is not included in this repository for security reasons.

### Setting up the model
To run the application, you need to:
1. Obtain the `model_full_ver7.json` file from the project administrators
2. Place it in the `backend/` directory
3. The application will automatically verify the model file's presence on startup

> Note: The model file contains sensitive information and should not be shared publicly.

## Deployment

### Frontend Deployment on Vercel

To deploy the frontend on Vercel:

1. Push your code to a GitHub repository
2. Go to [Vercel](https://vercel.com) and sign in with your GitHub account
3. Import your repository
4. Configure the deployment:
   - Framework Preset: Vue.js
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`
5. Set up environment variables:
   - Add `VITE_API_URL` with the URL of your deployed backend API 
   - (e.g., `https://your-api-domain.com`)

#### Notes on Frontend/Backend Separation

When deploying the frontend to Vercel, consider:
1. Your backend must be deployed separately (e.g., on a cloud service like Render, Heroku, or a VPS)
2. Update the `VITE_API_URL` environment variable in Vercel to point to that backend URL
3. Ensure your backend has CORS configured to accept requests from your Vercel frontend domain

### Backend Deployment

For backend deployment guidance, consult the documentation for your preferred hosting platform:
- [Render](https://render.com/docs)
- [Heroku](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-fastapi-app-with-gunicorn-on-ubuntu-20-04)
