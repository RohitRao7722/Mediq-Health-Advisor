"""
Test First Batch Processing

This script processes only the first batch of 50K chunks to verify
the batch processing system works correctly.
"""

import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Dict, Any
import logging
import time
import os
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_first_batch(chunked_docs_path: str = "chunked_documents.pkl",
                    batch_size: int = 50000,
                    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                    embedding_batch_size: int = 128):
    """
    Test processing the first batch of chunks.
    
    Args:
        chunked_docs_path: Path to chunked documents
        batch_size: Number of chunks to process (first batch)
        model_name: Model name to use
        embedding_batch_size: Batch size for embedding generation
    """
    
    # Force CPU usage
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    
    # Load chunked documents
    logger.info(f"Loading chunked documents from {chunked_docs_path}")
    with open(chunked_docs_path, 'rb') as f:
        chunked_docs = pickle.load(f)
    
    total_chunks = len(chunked_docs)
    logger.info(f"Total chunks available: {total_chunks:,}")
    
    # Take first batch
    first_batch = chunked_docs[:batch_size]
    logger.info(f"Processing first batch of {len(first_batch):,} chunks")
    
    # Load model
    logger.info(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name, device='cpu')
    
    # Optimize for CPU
    import torch
    torch.set_num_threads(4)
    
    embedding_dim = model.get_sentence_embedding_dimension()
    logger.info(f"Model loaded. Embedding dimension: {embedding_dim}")
    
    # Extract texts and metadata
    texts = [doc.page_content for doc in first_batch]
    metadata = [doc.metadata for doc in first_batch]
    
    # Generate embeddings
    logger.info("Generating embeddings...")
    start_time = time.time()
    
    embeddings = model.encode(
        texts,
        batch_size=embedding_batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    logger.info(f"Embeddings generated in {processing_time:.2f} seconds")
    logger.info(f"Processing speed: {len(first_batch)/processing_time:.2f} chunks/second")
    logger.info(f"Embedding shape: {embeddings.shape}")
    
    # Create FAISS index
    logger.info("Creating FAISS index...")
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
        "Mental health advice"
    ]
    
    print(f"\n{'='*80}")
    print("FIRST BATCH TEST RESULTS")
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
            if idx < len(first_batch):
                doc = first_batch[idx]
                print(f"Result {i} (Score: {score:.4f}):")
                print(f"  Source: {doc.metadata.get('source', 'Unknown')}")
                print(f"  Chunk: {doc.metadata.get('chunk_index', 'N/A')}/{doc.metadata.get('total_chunks', 'N/A')}")
                print(f"  Content preview: {doc.page_content[:150]}...")
                print()
    
    # Estimate full processing time
    total_batches = (total_chunks + batch_size - 1) // batch_size
    estimated_time_per_batch = processing_time
    estimated_total_time = estimated_time_per_batch * total_batches
    
    print(f"\n{'='*80}")
    print("FULL PROCESSING ESTIMATION")
    print(f"{'='*80}")
    print(f"Total chunks: {total_chunks:,}")
    print(f"Batch size: {batch_size:,}")
    print(f"Total batches: {total_batches}")
    print(f"First batch time: {processing_time:.2f} seconds ({processing_time/60:.1f} minutes)")
    print(f"Estimated total time: {estimated_total_time:.2f} seconds ({estimated_total_time/60:.1f} minutes)")
    print(f"Estimated processing speed: {total_chunks/estimated_total_time:.2f} chunks/second")
    
    # Save test results
    test_results = {
        "batch_size": len(first_batch),
        "processing_time": processing_time,
        "embedding_shape": embeddings.shape,
        "total_chunks": total_chunks,
        "total_batches": total_batches,
        "estimated_total_time": estimated_total_time,
        "model_name": model_name
    }
    
    with open("first_batch_test_results.pkl", "wb") as f:
        pickle.dump(test_results, f)
    
    logger.info("Test results saved to first_batch_test_results.pkl")
    
    # Save the first batch results for inspection
    with open("first_batch_embeddings.pkl", "wb") as f:
        pickle.dump(embeddings, f)
    
    with open("first_batch_metadata.pkl", "wb") as f:
        pickle.dump(metadata, f)
    
    # Save FAISS index
    faiss.write_index(index, "first_batch_index.idx")
    
    logger.info("First batch results saved:")
    logger.info("- first_batch_embeddings.pkl")
    logger.info("- first_batch_metadata.pkl") 
    logger.info("- first_batch_index.idx")
    
    return test_results


def main():
    """Main function to run first batch test."""
    
    # Configuration
    config = {
        "chunked_docs_path": "chunked_documents.pkl",
        "batch_size": 50000,  # First 50K chunks
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "embedding_batch_size": 128
    }
    
    logger.info("Starting first batch test...")
    logger.info(f"Configuration: {config}")
    
    try:
        results = test_first_batch(**config)
        
        print(f"\n✅ First batch test completed successfully!")
        print(f"📊 Results: {results}")
        
        print(f"\n{'='*80}")
        print("NEXT STEPS")
        print(f"{'='*80}")
        print("1. If first batch results look good, run: python src/batch_embedding_processor.py")
        print("2. This will process all remaining batches")
        print(f"3. Estimated total time: {results['estimated_total_time']/60:.1f} minutes")
        print("4. The batch processor will save checkpoints after each batch")
        
    except Exception as e:
        logger.error(f"Error in first batch test: {str(e)}")
        raise


if __name__ == "__main__":
    main()


