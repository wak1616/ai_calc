FROM python:3.12-slim

WORKDIR /app

# Install build deps for numpy/pandas/scikit-learn native extensions
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py XGBoost_smooth_model_latest.json ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
