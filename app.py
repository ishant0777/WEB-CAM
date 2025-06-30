import subprocess
import threading
import time
import sys
import os
from config import Config

def run_flask_backend():
    """Run Flask backend in a separate process"""
    try:
        subprocess.run([sys.executable, "flask_backend.py"], check=True)
    except KeyboardInterrupt:
        print("Flask backend stopped")
    except Exception as e:
        print(f"Error running Flask backend: {e}")

def run_streamlit_frontend():
    """Run Streamlit frontend"""
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_frontend.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("Streamlit frontend stopped")
    except Exception as e:
        print(f"Error running Streamlit frontend: {e}")

def main():
    print("🚀 Starting Multi-Camera Surveillance System...")
    print("=" * 50)
    
    # Create necessary directories
    os.makedirs(Config.RECORDING_PATH, exist_ok=True)
    
    # Start Flask backend in a separate thread
    flask_thread = threading.Thread(target=run_flask_backend, daemon=True)
    flask_thread.start()
    
    # Wait a moment for Flask to start
    print("⏳ Starting Flask backend...")
    time.sleep(3)
    
    # Start Streamlit frontend
    print("🌐 Starting Streamlit frontend...")
    print("📱 Access the app at: http://localhost:8501")
    print("🔧 Flask API at: http://localhost:5001")
    print("=" * 50)
    
    try:
        run_streamlit_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down surveillance system...")
        sys.exit(0)

if __name__ == "__main__":
    main()
