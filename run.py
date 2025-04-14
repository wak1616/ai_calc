import subprocess
import sys
from pathlib import Path
import threading
import time

def run_frontend():
    print("Starting frontend development server...")
    subprocess.run("npm run dev", shell=True, check=True)

def run_backend():
    # Check if model exists in backend directory
    model_file = "XGBoost_model_full.json"
    backend_dir = Path("backend")
    backend_model_path = backend_dir / model_file
    
    if not backend_model_path.exists():
        print(f"Error: {model_file} not found in backend directory!")
        print(f"Please ensure {model_file} is placed in the backend directory.")
        sys.exit(1)

    print("Starting backend server...")
    subprocess.run("uvicorn backend.main:app --reload", shell=True, check=True)

def main():
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()

    # Wait a moment for the backend to start
    time.sleep(2)

    # Start frontend (this will block until the frontend server stops)
    run_frontend()

if __name__ == "__main__":
    print("Starting Arcuate Incision Calculator...")
    print("Frontend will be available at: http://localhost:5173")
    print("Backend API will be available at: http://localhost:8000")
    main() 