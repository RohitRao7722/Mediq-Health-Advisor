"""
Test script to verify frontend setup
"""

import os
import subprocess
import sys
from pathlib import Path

def test_frontend_setup():
    """Test if frontend can be set up and built."""
    print("🧪 Testing Frontend Setup")
    print("=" * 40)
    
    # Check if frontend directory exists
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    print("✅ Frontend directory exists")
    
    # Check if package.json exists
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("❌ package.json not found")
        return False
    
    print("✅ package.json exists")
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("⚠️  node_modules not found - need to run npm install")
        return False
    
    print("✅ node_modules exists")
    
    # Check if key files exist
    key_files = [
        "src/App.tsx",
        "src/main.tsx",
        "src/components/ChatInterface.tsx",
        "src/store/chatStore.ts",
        "src/services/api.ts",
        "vite.config.ts",
        "tsconfig.json"
    ]
    
    for file_path in key_files:
        full_path = frontend_dir / file_path
        if not full_path.exists():
            print(f"❌ Missing file: {file_path}")
            return False
        print(f"✅ {file_path}")
    
    print("\n🎉 Frontend setup looks good!")
    print("\nTo start the frontend:")
    print("1. cd frontend")
    print("2. npm install (if not done)")
    print("3. npm run dev")
    
    return True

def test_backend_setup():
    """Test if backend can be set up."""
    print("\n🧪 Testing Backend Setup")
    print("=" * 40)
    
    # Check if enhanced_web_chatbot.py exists
    backend_file = Path("src/enhanced_web_chatbot.py")
    if not backend_file.exists():
        print("❌ enhanced_web_chatbot.py not found")
        return False
    
    print("✅ enhanced_web_chatbot.py exists")
    
    # Check if vector files exist
    vector_files = ["vector_index.idx", "vector_metadata.pkl"]
    for file_path in vector_files:
        if not Path(file_path).exists():
            print(f"❌ Missing vector file: {file_path}")
            return False
        print(f"✅ {file_path}")
    
    # Check if Groq API key is set
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  GROQ_API_KEY not set - backend won't work")
        return False
    
    print("✅ GROQ_API_KEY is set")
    
    print("\n🎉 Backend setup looks good!")
    print("\nTo start the backend:")
    print("python src/enhanced_web_chatbot.py")
    
    return True

def main():
    """Main test function."""
    print("🏥 Health Chatbot Frontend Test")
    print("=" * 50)
    
    frontend_ok = test_frontend_setup()
    backend_ok = test_backend_setup()
    
    print("\n" + "=" * 50)
    print("📊 Test Results")
    print("=" * 50)
    print(f"Frontend: {'✅ Ready' if frontend_ok else '❌ Issues'}")
    print(f"Backend: {'✅ Ready' if backend_ok else '❌ Issues'}")
    
    if frontend_ok and backend_ok:
        print("\n🎉 Everything is ready!")
        print("\nTo start the full application:")
        print("1. Terminal 1: python src/enhanced_web_chatbot.py")
        print("2. Terminal 2: cd frontend && npm run dev")
        print("3. Open: http://localhost:3000")
    else:
        print("\n⚠️  Some issues found. Please fix them before starting.")
    
    return frontend_ok and backend_ok

if __name__ == "__main__":
    main()

