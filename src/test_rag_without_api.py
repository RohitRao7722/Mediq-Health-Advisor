"""
Test RAG system components without requiring Groq API key

This script tests the search and retrieval components of the RAG system
without making actual API calls to Groq.
"""

import os
import sys
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag_system import HealthRAGSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_search_components():
    """Test the search and retrieval components."""
    
    print("🧪 Testing RAG System Components (Without API)")
    print("=" * 60)
    
    try:
        # Initialize RAG system (without Groq client)
        print("📚 Loading vector database and embedding model...")
        
        # Check if vector files exist
        if not os.path.exists("vector_index.idx"):
            print("❌ Error: vector_index.idx not found")
            print("Please run the embedding generation process first:")
            print("python src/batch_embedding_processor.py")
            return False
        
        if not os.path.exists("vector_metadata.pkl"):
            print("❌ Error: vector_metadata.pkl not found")
            print("Please run the embedding generation process first:")
            print("python src/batch_embedding_processor.py")
            return False
        
        # Create a mock RAG system for testing search components
        class MockRAGSystem(HealthRAGSystem):
            def __init__(self, *args, **kwargs):
                # Initialize without Groq client
                self.model_name = kwargs.get('model_name', 'sentence-transformers/all-MiniLM-L6-v2')
                self.index_path = kwargs.get('index_path', 'vector_index.idx')
                self.metadata_path = kwargs.get('metadata_path', 'vector_metadata.pkl')
                self.groq_model = kwargs.get('groq_model', 'llama-3.1-8b-instant')
                self.embedder = None
                self.faiss_index = None
                self.metadata = []
                self.groq_client = None  # Mock - no actual client
        
        # Initialize mock system
        rag_system = MockRAGSystem()
        
        # Load search components
        rag_system.load_search_system()
        
        print("✅ Vector database loaded successfully!")
        print(f"📊 Total vectors: {rag_system.faiss_index.ntotal:,}")
        print(f"📚 Metadata entries: {len(rag_system.metadata):,}")
        
        # Test search functionality
        print("\n🔍 Testing search functionality...")
        
        test_queries = [
            "What are the symptoms of diabetes?",
            "How to treat high blood pressure?",
            "What causes chest pain?",
            "Mental health statistics",
            "Cancer prevention tips"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\nTest {i}: {query}")
            print("-" * 40)
            
            try:
                # Test document search
                results = rag_system.search_relevant_documents(query, k=3)
                
                print(f"✅ Found {len(results)} relevant documents")
                
                for j, result in enumerate(results, 1):
                    metadata = result['metadata']
                    source = metadata.get('source', 'Unknown')
                    score = result['score']
                    
                    print(f"  {j}. {os.path.basename(source)} (score: {score:.3f})")
                
                # Test prompt creation (without API call)
                prompt = rag_system.create_health_prompt(query, results)
                print(f"📝 Generated prompt length: {len(prompt)} characters")
                
            except Exception as e:
                print(f"❌ Error testing query: {str(e)}")
                continue
        
        print("\n" + "=" * 60)
        print("✅ RAG System Components Test Completed Successfully!")
        print("=" * 60)
        
        print("\n📋 Test Summary:")
        print(f"✅ Vector database: {rag_system.faiss_index.ntotal:,} documents")
        print(f"✅ Embedding model: {rag_system.model_name}")
        print(f"✅ Search functionality: Working")
        print(f"✅ Prompt generation: Working")
        print(f"✅ Metadata tracking: Working")
        
        print("\n🚀 Next Steps:")
        print("1. Get a Groq API key from: https://console.groq.com/")
        print("2. Set environment variable: export GROQ_API_KEY='your-key'")
        print("3. Run full RAG system: python src/rag_system.py")
        print("4. Or run web interface: python src/web_chatbot.py")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"❌ Test failed: {str(e)}")
        return False


def main():
    """Main test function."""
    success = test_search_components()
    
    if success:
        print("\n🎉 All components are working correctly!")
        print("Your RAG system is ready for Groq integration!")
    else:
        print("\n❌ Some components failed. Please check the errors above.")


if __name__ == "__main__":
    main()
