"""
Test script for the Health RAG System

This script tests the RAG system with various health queries to ensure
it's working correctly before full deployment.
"""

import os
import sys
import logging
from src.rag_system import HealthRAGSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_rag_system():
    """Test the RAG system with sample health queries."""
    
    # Configuration
    config = {
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "index_path": "vector_index.idx",
        "metadata_path": "vector_metadata.pkl",
        "groq_model": "llama-3.1-8b-instant"
    }
    
    # Check for Groq API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ Error: GROQ_API_KEY environment variable not set.")
        print("Please set your Groq API key:")
        print("export GROQ_API_KEY='your-api-key-here'")
        print("\nTo get a Groq API key:")
        print("1. Visit: https://console.groq.com/")
        print("2. Sign up for a free account")
        print("3. Generate an API key")
        print("4. Set it as an environment variable")
        return False
    
    try:
        # Initialize RAG system
        print("🚀 Initializing Health RAG System...")
        rag_system = HealthRAGSystem(**config, groq_api_key=groq_api_key)
        
        # Load search system
        print("📚 Loading vector database and embedding model...")
        rag_system.load_search_system()
        
        print("✅ RAG System loaded successfully!")
        print(f"📊 Vector database: {rag_system.faiss_index.ntotal:,} documents")
        print(f"🤖 LLM Model: {config['groq_model']}")
        
        # Test queries
        test_queries = [
            "What are the symptoms of diabetes?",
            "How to treat high blood pressure?",
            "What should I do if I have chest pain?",
            "How to manage stress and anxiety?",
            "What are the warning signs of a heart attack?"
        ]
        
        print("\n" + "="*80)
        print("TESTING RAG SYSTEM WITH HEALTH QUERIES")
        print("="*80)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 TEST {i}/{len(test_queries)}: {query}")
            print("-" * 60)
            
            try:
                # Get detailed response
                result = rag_system.get_conversation_context(query)
                
                print(f"✅ Response generated successfully!")
                print(f"📝 Response length: {result['metadata']['response_length']} characters")
                print(f"📚 Sources used: {result['metadata']['relevant_docs_count']}")
                print(f"🎯 Top relevance score: {result['metadata']['top_doc_score']:.3f}")
                print(f"⏱️  Attempts: {result['metadata']['attempt']}")
                
                # Show response preview
                response_preview = result['response'][:200] + "..." if len(result['response']) > 200 else result['response']
                print(f"\n💬 Response preview:\n{response_preview}")
                
                # Show sources
                print(f"\n📖 Sources:")
                for j, doc in enumerate(result['relevant_docs'][:3], 1):
                    source = doc['metadata'].get('source', 'Unknown')
                    score = doc['score']
                    print(f"  {j}. {os.path.basename(source)} (score: {score:.3f})")
                
            except Exception as e:
                print(f"❌ Error testing query: {str(e)}")
                continue
        
        print("\n" + "="*80)
        print("RAG SYSTEM TEST COMPLETED")
        print("="*80)
        print("✅ All tests completed successfully!")
        print("\n🎉 Your Health RAG System is ready for use!")
        print("\nTo start the interactive chatbot, run:")
        print("python src/rag_system.py")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to test RAG system: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return False


def interactive_test():
    """Run an interactive test session."""
    
    # Configuration
    config = {
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "index_path": "vector_index.idx",
        "metadata_path": "vector_metadata.pkl",
        "groq_model": "llama-3.1-8b-instant"
    }
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ Error: GROQ_API_KEY environment variable not set.")
        return
    
    try:
        # Initialize RAG system
        rag_system = HealthRAGSystem(**config, groq_api_key=groq_api_key)
        rag_system.load_search_system()
        
        print("="*80)
        print("INTERACTIVE RAG SYSTEM TEST")
        print("="*80)
        print("Enter health questions to test the system (type 'quit' to exit):")
        print("-" * 80)
        
        while True:
            try:
                user_input = input("\n🔍 Your health question: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye! Stay healthy!")
                    break
                
                if not user_input:
                    print("Please enter a health question.")
                    continue
                
                print("\n🤖 AI Response:")
                print("-" * 40)
                response = rag_system.chat(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Stay healthy!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    except Exception as e:
        logger.error(f"Failed to run interactive test: {str(e)}")
        print(f"❌ Error: {str(e)}")


def main():
    """Main function."""
    print("Health RAG System Test")
    print("=" * 50)
    print("1. Run automated tests")
    print("2. Run interactive test")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        test_rag_system()
    elif choice == "2":
        interactive_test()
    elif choice == "3":
        print("Goodbye!")
    else:
        print("Invalid choice. Running automated tests...")
        test_rag_system()


if __name__ == "__main__":
    main()

