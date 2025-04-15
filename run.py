import subprocess
import sys
import os
from pathlib import Path
import threading
import time
import uvicorn

def run_frontend():
    print("Starting frontend development server...")
    subprocess.run("npm run dev", shell=True, check=True)

def run_backend(dev_mode=True):
    # Check if model exists in backend directory
    model_file = "XGBoost_model_full.json"
    backend_dir = Path("backend")
    backend_model_path = backend_dir / model_file
    
    if not backend_model_path.exists():
        print(f"Error: {model_file} not found in backend directory!")
        print(f"Please ensure {model_file} is placed in the backend directory.")
        sys.exit(1)

    print("Starting backend server...")
    if dev_mode:
        # Development mode with hot reload
        subprocess.run("uvicorn backend.main:app --reload", shell=True, check=True)
    else:
        # Production mode
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)

def dev():
    print("\nStarting Development Servers...")
    print("Frontend will be available at: http://localhost:5173")
    print("Backend API will be available at: http://localhost:8000\n")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, args=(True,), daemon=True)
    backend_thread.start()

    # Wait a moment for the backend to start
    time.sleep(2)

    # Start frontend (this will block until the frontend server stops)
    run_frontend()

def prod():
    print("\nStarting Production Server...")
    print("Backend API will be available at: http://localhost:8000\n")
    run_backend(dev_mode=False)

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "prod":
        prod()
    else:
        dev() 