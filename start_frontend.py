"""
Startup script for the Health Chatbot Frontend

This script helps users start both the backend and frontend services.
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_requirements():
    """Check if all requirements are installed."""
    print("🔍 Checking requirements...")
    
    # Check if Groq API key is set
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Error: GROQ_API_KEY environment variable not set.")
        print("Please set your Groq API key:")
        print("export GROQ_API_KEY='your-api-key-here'")
        return False
    
    # Check if vector files exist
    if not os.path.exists("vector_index.idx") or not os.path.exists("vector_metadata.pkl"):
        print("❌ Error: Vector database files not found.")
        print("Please run the embedding generation process first:")
        print("python src/batch_embedding_processor.py")
        return False
    
    # Check if frontend directory exists
    if not os.path.exists("frontend"):
        print("❌ Error: Frontend directory not found.")
        print("Please ensure the frontend directory exists.")
        return False
    
    print("✅ All requirements satisfied!")
    return True

def install_frontend_dependencies():
    """Install frontend dependencies."""
    print("📦 Installing frontend dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "flask", "flask-cors"
        ])
        
        # Install frontend dependencies
        frontend_dir = Path("frontend")
        if frontend_dir.exists():
            subprocess.check_call([
                "npm", "install"
            ], cwd=frontend_dir)
        
        print("✅ Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js and npm first.")
        return False

def start_backend():
    """Start the backend server."""
    print("🚀 Starting backend server...")
    
    try:
        subprocess.Popen([
            sys.executable, "src/enhanced_web_chatbot.py"
        ])
        print("✅ Backend server started on http://localhost:5000")
        return True
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    """Start the frontend development server."""
    print("🎨 Starting frontend development server...")
    
    try:
        frontend_dir = Path("frontend")
        if frontend_dir.exists():
            subprocess.Popen([
                "npm", "run", "dev"
            ], cwd=frontend_dir)
            print("✅ Frontend server started on http://localhost:3000")
            return True
        else:
            print("❌ Frontend directory not found")
            return False
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def wait_for_services():
    """Wait for services to be ready."""
    print("⏳ Waiting for services to start...")
    time.sleep(5)
    
    # Try to open browser
    try:
        webbrowser.open("http://localhost:3000")
        print("🌐 Opening browser...")
    except:
        print("🌐 Please open http://localhost:3000 in your browser")

def main():
    """Main startup function."""
    print("🏥 Health Chatbot Frontend Startup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Install dependencies
    if not install_frontend_dependencies():
        return
    
    # Start backend
    if not start_backend():
        return
    
    # Wait a moment for backend to start
    time.sleep(2)
    
    # Start frontend
    if not start_frontend():
        return
    
    # Wait for services and open browser
    wait_for_services()
    
    print("\n🎉 Health Chatbot is now running!")
    print("=" * 50)
    print("📱 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down services...")
        print("Goodbye!")

if __name__ == "__main__":
    main()

