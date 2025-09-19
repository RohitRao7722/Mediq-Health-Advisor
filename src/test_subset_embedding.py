"""
Test Script for Subset Embedding Generation

This script processes only a subset of chunks to test the embedding pipeline
before running on the full dataset.
"""

import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Dict, Any
import logging
import time
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_subset_embedding(chunked_docs_path: str = "chunked_documents.pkl",
                         subset_size: int = 10000,
                         model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                         batch_size: int = 128):
    """
    Test embedding generation with a subset of chunks.
    
    Args:
        chunked_docs_path: Path to chunked documents
        subset_size: Number of chunks to process for testing
        model_name: Model name to use
        batch_size: Batch size for processing
    """
    
    # Force CPU usage
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    
    # Load chunked documents
    logger.info(f"Loading chunked documents from {chunked_docs_path}")
    with open(chunked_docs_path, 'rb') as f:
        chunked_docs = pickle.load(f)
    
    logger.info(f"Total chunks available: {len(chunked_docs):,}")
    
    # Take subset for testing
    subset_docs = chunked_docs[:subset_size]
    logger.info(f"Processing subset of {len(subset_docs):,} chunks for testing")
    
    # Load model
    logger.info(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name, device='cpu')
    
    # Optimize for CPU
    import torch
    torch.set_num_threads(4)
    
    # Extract texts
    texts = [doc.page_content for doc in subset_docs]
    
    # Generate embeddings
    logger.info("Generating embeddings...")
    start_time = time.time()
    
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    logger.info(f"Embeddings generated in {processing_time:.2f} seconds")
    logger.info(f"Processing speed: {len(subset_docs)/processing_time:.2f} chunks/second")
    logger.info(f"Embedding shape: {embeddings.shape}")
    
    # Create FAISS index
    logger.info("Creating FAISS index...")
    embedding_dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(embeddings.astype('float32'))
    
    logger.info(f"FAISS index created with {index.ntotal} vectors")
    
    # Test search functionality
    logger.info("Testing search functionality...")
    test_queries = [
        "What are the symptoms of diabetes?",
        "How to treat depression?",
        "Blood pressure medication",
        "Cancer prevention tips",
        "Mental health statistics"
    ]
    
    print(f"\n{'='*80}")
    print("SUBSET TEST RESULTS")
    print(f"{'='*80}")
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 50)
        
        # Generate query embedding
        query_embedding = model.encode([query], convert_to_numpy=True)
        
        # Search
        start_search = time.time()
        scores, indices = index.search(query_embedding.astype('float32'), 3)
        search_time = time.time() - start_search
        
        print(f"Search time: {search_time:.4f} seconds")
        
        for i, (score, idx) in enumerate(zip(scores[0], indices[0]), 1):
            if idx < len(subset_docs):
                doc = subset_docs[idx]
                print(f"Result {i} (Score: {score:.4f}):")
                print(f"  Source: {doc.metadata.get('source', 'Unknown')}")
                print(f"  Content preview: {doc.page_content[:200]}...")
                print()
    
    # Estimate full processing time
    total_chunks = len(chunked_docs)
    estimated_time = (total_chunks / len(subset_docs)) * processing_time
    
    print(f"\n{'='*80}")
    print("FULL DATASET ESTIMATION")
    print(f"{'='*80}")
    print(f"Total chunks to process: {total_chunks:,}")
    print(f"Subset processed: {len(subset_docs):,}")
    print(f"Subset processing time: {processing_time:.2f} seconds")
    print(f"Estimated full processing time: {estimated_time:.2f} seconds ({estimated_time/60:.1f} minutes)")
    print(f"Estimated processing speed: {total_chunks/estimated_time:.2f} chunks/second")
    
    # Save test results
    test_results = {
        "subset_size": len(subset_docs),
        "processing_time": processing_time,
        "embedding_shape": embeddings.shape,
        "estimated_full_time": estimated_time,
        "model_name": model_name
    }
    
    with open("test_results.pkl", "wb") as f:
        pickle.dump(test_results, f)
    
    logger.info("Test results saved to test_results.pkl")
    
    return test_results


def main():
    """Main function to run subset test."""
    
    # Configuration
    config = {
        "subset_size": 10000,  # Test with 10K chunks
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "batch_size": 128
    }
    
    logger.info("Starting subset embedding test...")
    logger.info(f"Configuration: {config}")
    
    try:
        results = test_subset_embedding(**config)
        
        print(f"\n✅ Subset test completed successfully!")
        print(f"📊 Results: {results}")
        
        # Ask if user wants to proceed with full processing
        print(f"\n{'='*80}")
        print("NEXT STEPS")
        print(f"{'='*80}")
        print("1. If test results look good, run: python src/optimized_embedding_and_vectorstore.py")
        print("2. This will process all 303,409 chunks")
        print(f"3. Estimated time: {results['estimated_full_time']/60:.1f} minutes")
        
    except Exception as e:
        logger.error(f"Error in subset test: {str(e)}")
        raise


if __name__ == "__main__":
    main()


