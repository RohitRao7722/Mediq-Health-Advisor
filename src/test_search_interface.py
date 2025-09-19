"""
Health Chatbot Search Interface

This script provides a comprehensive testing interface for the vector database
with various health-related queries to verify search quality and relevance.
"""

import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Dict, Any
import logging
import time
import os
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthSearchInterface:
    """
    Interface for testing health-related search functionality.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 index_path: str = "vector_index.idx",
                 metadata_path: str = "vector_metadata.pkl"):
        """
        Initialize the search interface.
        
        Args:
            model_name: Sentence transformer model name
            index_path: Path to FAISS index
            metadata_path: Path to metadata file
        """
        self.model_name = model_name
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.model = None
        self.faiss_index = None
        self.metadata = []
        
        # Force CPU usage
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        
    def load_search_system(self):
        """Load the search system components."""
        logger.info("Loading search system...")
        
        # Load model
        logger.info(f"Loading model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name, device='cpu')
        
        # Optimize for CPU
        import torch
        torch.set_num_threads(4)
        
        # Load FAISS index
        logger.info(f"Loading FAISS index from {self.index_path}")
        self.faiss_index = faiss.read_index(self.index_path)
        
        # Load metadata
        logger.info(f"Loading metadata from {self.metadata_path}")
        with open(self.metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)
        
        logger.info(f"Search system loaded successfully!")
        logger.info(f"Index vectors: {self.faiss_index.ntotal:,}")
        logger.info(f"Metadata entries: {len(self.metadata):,}")
        
    def search(self, query: str, k: int = 5, show_content: bool = True) -> List[Dict]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            k: Number of results to return
            show_content: Whether to show content preview
            
        Returns:
            List of search results
        """
        if self.faiss_index is None:
            raise ValueError("Search system not loaded. Call load_search_system() first.")
        
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search in FAISS index
        start_time = time.time()
        scores, indices = self.faiss_index.search(query_embedding.astype('float32'), k)
        search_time = time.time() - start_time
        
        # Format results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0]), 1):
            if idx < len(self.metadata):
                result = {
                    'rank': i,
                    'score': float(score),
                    'metadata': self.metadata[idx],
                    'search_time': search_time
                }
                
                if show_content:
                    # Get content from metadata if available
                    source = self.metadata[idx].get('source', 'Unknown')
                    if 'ai-medical-chatbot.csv' in source:
                        result['content_type'] = 'Medical Q&A'
                    elif 'medquad.csv' in source:
                        result['content_type'] = 'Medical Knowledge'
                    elif 'NIH' in source:
                        result['content_type'] = 'NIH Health Topic'
                    elif 'who' in source:
                        result['content_type'] = 'WHO Document'
                    else:
                        result['content_type'] = 'Health Data'
                
                results.append(result)
        
        return results
    
    def display_results(self, query: str, results: List[Dict], max_content_length: int = 200):
        """Display search results in a formatted way."""
        print(f"\n{'='*80}")
        print(f"SEARCH QUERY: '{query}'")
        print(f"{'='*80}")
        print(f"Search time: {results[0]['search_time']:.4f} seconds")
        print(f"Results found: {len(results)}")
        print()
        
        for result in results:
            metadata = result['metadata']
            print(f"Rank {result['rank']} (Score: {result['score']:.4f})")
            print(f"Content Type: {result.get('content_type', 'Unknown')}")
            print(f"Source: {metadata.get('source', 'Unknown')}")
            print(f"Chunk: {metadata.get('chunk_index', 'N/A')}/{metadata.get('total_chunks', 'N/A')}")
            print(f"Size: {metadata.get('chunk_size', 'N/A')} characters")
            print("-" * 80)
    
    def test_health_queries(self):
        """Test with a comprehensive set of health queries."""
        
        # Comprehensive health query test suite
        test_queries = [
            # General Health
            "What are the symptoms of diabetes?",
            "How to treat high blood pressure?",
            "What causes chest pain?",
            "How to prevent heart disease?",
            
            # Mental Health
            "How to treat depression?",
            "What are anxiety symptoms?",
            "Mental health statistics",
            "How to manage stress?",
            
            # Specific Conditions
            "Cancer prevention tips",
            "How to treat asthma?",
            "What is hypertension?",
            "Diabetes management",
            
            # Medications
            "Blood pressure medication",
            "Diabetes medication side effects",
            "Antidepressant treatment",
            "Pain management drugs",
            
            # Symptoms
            "Headache causes and treatment",
            "Fever symptoms and treatment",
            "Cough and cold remedies",
            "Digestive problems",
            
            # Prevention
            "How to maintain healthy weight?",
            "Exercise for heart health",
            "Healthy diet recommendations",
            "Sleep hygiene tips",
            
            # Emergency
            "Heart attack symptoms",
            "Stroke warning signs",
            "When to call emergency?",
            "First aid for injuries"
        ]
        
        print(f"\n{'='*80}")
        print("COMPREHENSIVE HEALTH QUERY TEST")
        print(f"{'='*80}")
        print(f"Testing {len(test_queries)} health queries...")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test each query
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*60}")
            print(f"TEST {i}/{len(test_queries)}: {query}")
            print(f"{'='*60}")
            
            try:
                results = self.search(query, k=3, show_content=True)
                self.display_results(query, results)
                
                # Brief pause between queries
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error testing query '{query}': {str(e)}")
        
        print(f"\n{'='*80}")
        print("HEALTH QUERY TEST COMPLETED")
        print(f"{'='*80}")
    
    def interactive_search(self):
        """Interactive search mode for manual testing."""
        print(f"\n{'='*80}")
        print("INTERACTIVE HEALTH SEARCH")
        print(f"{'='*80}")
        print("Enter health-related queries to test the search system.")
        print("Type 'quit' to exit.")
        print()
        
        while True:
            try:
                query = input("Enter your health query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not query:
                    print("Please enter a query.")
                    continue
                
                results = self.search(query, k=5, show_content=True)
                self.display_results(query, results)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def benchmark_search_performance(self, num_queries: int = 100):
        """Benchmark search performance with random queries."""
        logger.info(f"Running search performance benchmark with {num_queries} queries...")
        
        # Sample queries for benchmarking
        sample_queries = [
            "diabetes symptoms", "blood pressure", "depression treatment",
            "cancer prevention", "heart disease", "asthma management",
            "headache causes", "fever treatment", "exercise benefits",
            "healthy diet", "sleep problems", "stress management"
        ]
        
        search_times = []
        
        for i in range(num_queries):
            query = sample_queries[i % len(sample_queries)]
            
            start_time = time.time()
            results = self.search(query, k=5, show_content=False)
            search_time = time.time() - start_time
            
            search_times.append(search_time)
            
            if (i + 1) % 20 == 0:
                logger.info(f"Completed {i + 1}/{num_queries} queries")
        
        # Calculate statistics
        avg_search_time = np.mean(search_times)
        min_search_time = np.min(search_times)
        max_search_time = np.max(search_times)
        
        print(f"\n{'='*80}")
        print("SEARCH PERFORMANCE BENCHMARK")
        print(f"{'='*80}")
        print(f"Queries tested: {num_queries}")
        print(f"Average search time: {avg_search_time:.4f} seconds")
        print(f"Min search time: {min_search_time:.4f} seconds")
        print(f"Max search time: {max_search_time:.4f} seconds")
        print(f"Queries per second: {1/avg_search_time:.2f}")


def main():
    """Main function to run search tests."""
    
    # Configuration
    config = {
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "index_path": "vector_index.idx",
        "metadata_path": "vector_metadata.pkl"
    }
    
    # Create search interface
    search_interface = HealthSearchInterface(**config)
    
    try:
        # Load search system
        search_interface.load_search_system()
        
        print("Choose testing mode:")
        print("1. Comprehensive health query test")
        print("2. Interactive search mode")
        print("3. Performance benchmark")
        print("4. All tests")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            search_interface.test_health_queries()
        elif choice == "2":
            search_interface.interactive_search()
        elif choice == "3":
            search_interface.benchmark_search_performance()
        elif choice == "4":
            search_interface.test_health_queries()
            search_interface.benchmark_search_performance()
            print("\nAll tests completed!")
        else:
            print("Invalid choice. Running comprehensive test...")
            search_interface.test_health_queries()
        
    except Exception as e:
        logger.error(f"Error in search testing: {str(e)}")
        raise


if __name__ == "__main__":
    main()

