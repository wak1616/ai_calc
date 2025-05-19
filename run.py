import subprocess
import sys
import os
from pathlib import Path
import threading
import time
import uvicorn
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

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
    # Find an available port starting from 8000
    port = 8000
    max_port_attempts = 10  # Try up to 10 different ports
    
    for _ in range(max_port_attempts):
        if not is_port_in_use(port):
            break
        print(f"Port {port} is already in use, trying port {port+1}...")
        port += 1
    
    if dev_mode:
        # Development mode with hot reload
        try:
            subprocess.run(f"uvicorn backend.main:app --reload --port {port}", shell=True, check=True)
        except subprocess.CalledProcessError:
            print(f"Failed to start backend server on port {port}. Is it already running?")
            sys.exit(1)
    else:
        # Production mode
        port = int(os.environ.get("PORT", port))
        uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)

def dev():
    print("\nStarting Development Servers...")
    print("Frontend will be available at: http://localhost:5173")
    
    # Find an available port for backend
    port = 8000
    while is_port_in_use(port):
        port += 1
    
    print(f"Backend API will be available at: http://localhost:{port}\n")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, args=(True,), daemon=True)
    backend_thread.start()

    # Wait a moment for the backend to start
    time.sleep(2)

    # Start frontend (this will block until the frontend server stops)
    run_frontend()

def prod():
    print("\nStarting Production Server...")
    
    # Find an available port for backend
    port = 8000
    while is_port_in_use(port):
        port += 1
    
    print(f"Backend API will be available at: http://localhost:{port}\n")
    run_backend(dev_mode=False)

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "prod":
        prod()
    else:
        dev() 