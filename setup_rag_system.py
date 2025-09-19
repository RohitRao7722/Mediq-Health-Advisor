"""
Setup script for the Health RAG System

This script helps users set up the RAG system by:
1. Installing required dependencies
2. Checking for Groq API key
3. Testing the system
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing required dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_groq_api_key():
    """Check if Groq API key is available."""
    print("\n🔑 Checking for Groq API key...")
    
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        print("✅ Groq API key found!")
        return True
    else:
        print("❌ Groq API key not found!")
        print("\nTo get a Groq API key:")
        print("1. Visit: https://console.groq.com/")
        print("2. Sign up for a free account")
        print("3. Generate an API key")
        print("4. Set it as an environment variable:")
        print("   export GROQ_API_KEY='your-api-key-here'")
        print("\nOr create a .env file with:")
        print("   GROQ_API_KEY=your-api-key-here")
        return False


def check_vector_files():
    """Check if vector database files exist."""
    print("\n📚 Checking for vector database files...")
    
    required_files = ["vector_index.idx", "vector_metadata.pkl"]
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} missing")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        print("Please run the embedding generation process first:")
        print("python src/batch_embedding_processor.py")
        return False
    
    print("✅ All vector database files found!")
    return True


def test_system():
    """Test the RAG system."""
    print("\n🧪 Testing RAG system...")
    
    try:
        from src.test_rag_system import test_rag_system
        success = test_rag_system()
        return success
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main setup function."""
    print("🏥 Health RAG System Setup")
    print("=" * 50)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        return
    
    # Step 2: Check Groq API key
    if not check_groq_api_key():
        print("❌ Setup failed: Groq API key required")
        return
    
    # Step 3: Check vector files
    if not check_vector_files():
        print("❌ Setup failed: Vector database files required")
        return
    
    # Step 4: Test system
    print("\n🚀 Running system test...")
    if test_system():
        print("\n🎉 Setup completed successfully!")
        print("\nYour Health RAG System is ready to use!")
        print("\nTo start the chatbot, run:")
        print("python src/rag_system.py")
        print("\nOr run tests with:")
        print("python src/test_rag_system.py")
    else:
        print("❌ Setup completed but system test failed")
        print("Please check the error messages above")


if __name__ == "__main__":
    main()

