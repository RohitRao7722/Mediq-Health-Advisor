"""
Optimized Embedding Generation and Vector Store for CPU-Only Systems

This module uses quantized models optimized for CPU inference, specifically designed
for i5 processors without GPU requirements.
"""

import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Dict, Any
import logging
import os
from tqdm import tqdm
import time
import torch

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptimizedHealthVectorStore:
    """
    An optimized vector store class for health-related document embeddings with CPU-optimized models.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the vector store with a sentence transformer model.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.embedder = None
        self.faiss_index = None
        self.metadata = []
        self.embedding_dim = None
        
    def load_embedding_model(self):
        """Load the sentence transformer model with CPU optimization."""
        logger.info(f"Loading optimized embedding model: {self.model_name}")
        
        # Force CPU usage and disable GPU
        import os
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        
        # Load model with CPU optimization
        self.embedder = SentenceTransformer(
            self.model_name,
            device='cpu',  # Force CPU usage
            cache_folder='./model_cache'  # Local cache
        )
        
        # Optimize for CPU inference
        self.embedder.eval()
        torch.set_num_threads(4)  # Optimize for i5 CPU
        
        self.embedding_dim = self.embedder.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")
        logger.info(f"Model device: {self.embedder.device}")
        
    def generate_embeddings_optimized(self, chunked_docs: List, 
                                    batch_size: int = 128,  # Smaller batch for CPU
                                    show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for all chunked documents with CPU optimization.
        
        Args:
            chunked_docs: List of chunked Document objects
            batch_size: Batch size for embedding generation (smaller for CPU)
            show_progress: Whether to show progress bar
            
        Returns:
            numpy array of embeddings
        """
        if self.embedder is None:
            self.load_embedding_model()
            
        logger.info(f"Generating embeddings for {len(chunked_docs)} chunks...")
        logger.info(f"Using batch size: {batch_size} (optimized for CPU)")
        
        # Extract text content
        texts = [doc.page_content for doc in chunked_docs]
        
        # Generate embeddings with CPU optimization
        start_time = time.time()
        
        # Process in smaller batches for CPU efficiency
        all_embeddings = []
        for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self.embedder.encode(
                batch_texts,
                convert_to_numpy=True,
                show_progress_bar=False,
                batch_size=min(batch_size, len(batch_texts))
            )
            all_embeddings.append(batch_embeddings)
        
        # Combine all embeddings
        embeddings = np.vstack(all_embeddings)
        
        end_time = time.time()
        logger.info(f"Embeddings generated in {end_time - start_time:.2f} seconds")
        logger.info(f"Embedding shape: {embeddings.shape}")
        logger.info(f"Processing speed: {len(chunked_docs)/(end_time - start_time):.2f} chunks/second")
        
        return embeddings
    
    def create_faiss_index(self, embeddings: np.ndarray, 
                          index_type: str = "flat") -> faiss.Index:
        """
        Create FAISS index from embeddings.
        
        Args:
            embeddings: numpy array of embeddings
            index_type: Type of FAISS index ("flat" or "ivf")
            
        Returns:
            FAISS index
        """
        logger.info(f"Creating FAISS {index_type} index...")
        
        embedding_dim = embeddings.shape[1]
        
        if index_type == "flat":
            # Simple L2 distance index - good for small to medium datasets
            index = faiss.IndexFlatL2(embedding_dim)
        elif index_type == "ivf":
            # Inverted file index - better for large datasets
            nlist = min(100, len(embeddings) // 100)  # Number of clusters
            quantizer = faiss.IndexFlatL2(embedding_dim)
            index = faiss.IndexIVFFlat(quantizer, embedding_dim, nlist)
            index.train(embeddings)
        else:
            raise ValueError(f"Unsupported index type: {index_type}")
        
        # Add embeddings to index
        index.add(embeddings.astype('float32'))
        
        logger.info(f"FAISS index created with {index.ntotal} vectors")
        self.faiss_index = index
        
        return index
    
    def search(self, query: str, k: int = 5) -> List[Tuple[float, Dict]]:
        """
        Search for similar documents using a query string.
        
        Args:
            query: Query string
            k: Number of results to return
            
        Returns:
            List of (score, metadata) tuples
        """
        if self.faiss_index is None:
            raise ValueError("FAISS index not initialized. Call create_faiss_index first.")
        
        if self.embedder is None:
            self.load_embedding_model()
        
        # Generate embedding for query
        query_embedding = self.embedder.encode([query], convert_to_numpy=True)
        
        # Search in FAISS index
        scores, indices = self.faiss_index.search(query_embedding.astype('float32'), k)
        
        # Return results with metadata
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata):
                results.append((float(score), self.metadata[idx]))
        
        return results
    
    def save_vector_store(self, index_path: str = "vector_index.idx", 
                         metadata_path: str = "vector_metadata.pkl"):
        """
        Save the vector store to disk.
        
        Args:
            index_path: Path to save FAISS index
            metadata_path: Path to save metadata
        """
        if self.faiss_index is None:
            raise ValueError("No FAISS index to save")
        
        logger.info(f"Saving FAISS index to {index_path}")
        faiss.write_index(self.faiss_index, index_path)
        
        logger.info(f"Saving metadata to {metadata_path}")
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        logger.info("Vector store saved successfully")
    
    def load_vector_store(self, index_path: str = "vector_index.idx", 
                         metadata_path: str = "vector_metadata.pkl"):
        """
        Load the vector store from disk.
        
        Args:
            index_path: Path to FAISS index
            metadata_path: Path to metadata
        """
        logger.info(f"Loading FAISS index from {index_path}")
        self.faiss_index = faiss.read_index(index_path)
        
        logger.info(f"Loading metadata from {metadata_path}")
        with open(metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)
        
        logger.info(f"Loaded vector store with {self.faiss_index.ntotal} vectors")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        if self.faiss_index is None:
            return {"error": "No vector store loaded"}
        
        return {
            "total_vectors": self.faiss_index.ntotal,
            "embedding_dimension": self.embedding_dim,
            "model_name": self.model_name,
            "index_type": type(self.faiss_index).__name__
        }


def create_optimized_vector_store(chunked_docs_path: str = "chunked_documents.pkl",
                                model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                                batch_size: int = 128,
                                index_type: str = "flat") -> OptimizedHealthVectorStore:
    """
    Create an optimized vector store from chunked documents.
    
    Args:
        chunked_docs_path: Path to chunked documents pickle file
        model_name: Sentence transformer model name
        batch_size: Batch size for embedding generation (optimized for CPU)
        index_type: Type of FAISS index
        
    Returns:
        OptimizedHealthVectorStore instance
    """
    # Load chunked documents
    logger.info(f"Loading chunked documents from {chunked_docs_path}")
    with open(chunked_docs_path, 'rb') as f:
        chunked_docs = pickle.load(f)
    
    logger.info(f"Loaded {len(chunked_docs)} chunked documents")
    
    # Create vector store
    vector_store = OptimizedHealthVectorStore(model_name=model_name)
    
    # Generate embeddings
    embeddings = vector_store.generate_embeddings_optimized(
        chunked_docs, 
        batch_size=batch_size
    )
    
    # Store metadata
    vector_store.metadata = [doc.metadata for doc in chunked_docs]
    
    # Create FAISS index
    vector_store.create_faiss_index(embeddings, index_type=index_type)
    
    return vector_store


def estimate_processing_time(num_chunks: int, batch_size: int = 128) -> Dict[str, float]:
    """
    Estimate processing time based on chunk count and batch size.
    
    Args:
        num_chunks: Number of chunks to process
        batch_size: Batch size for processing
        
    Returns:
        Dictionary with time estimates
    """
    # Conservative estimates based on i5 CPU performance
    chunks_per_second = 50  # Conservative estimate for i5 CPU
    total_seconds = num_chunks / chunks_per_second
    
    return {
        "total_chunks": num_chunks,
        "estimated_seconds": total_seconds,
        "estimated_minutes": total_seconds / 60,
        "estimated_hours": total_seconds / 3600,
        "chunks_per_second": chunks_per_second
    }


def test_vector_search(vector_store: OptimizedHealthVectorStore, 
                      test_queries: List[str] = None) -> None:
    """
    Test the vector search functionality with sample queries.
    
    Args:
        vector_store: OptimizedHealthVectorStore instance
        test_queries: List of test queries
    """
    if test_queries is None:
        test_queries = [
            "What are the symptoms of diabetes?",
            "How to treat depression?",
            "Mental health statistics",
            "Blood pressure medication",
            "Cancer prevention tips"
        ]
    
    print(f"\n{'='*80}")
    print("OPTIMIZED VECTOR SEARCH TEST RESULTS")
    print(f"{'='*80}")
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 50)
        
        try:
            start_time = time.time()
            results = vector_store.search(query, k=3)
            search_time = time.time() - start_time
            
            print(f"Search time: {search_time:.4f} seconds")
            
            for i, (score, metadata) in enumerate(results, 1):
                print(f"Result {i} (Score: {score:.4f}):")
                print(f"  Source: {metadata.get('source', 'Unknown')}")
                print(f"  Chunk: {metadata.get('chunk_index', 'N/A')}/{metadata.get('total_chunks', 'N/A')}")
                print(f"  Size: {metadata.get('chunk_size', 'N/A')} chars")
                print()
                
        except Exception as e:
            print(f"Error searching for '{query}': {str(e)}")


def main():
    """Main function to create and test the optimized vector store."""
    
    # Configuration optimized for i5 CPU
    config = {
        "chunked_docs_path": "chunked_documents.pkl",
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",  # Fast and efficient model
        "batch_size": 128,  # Optimized for CPU
        "index_type": "flat",  # Use "ivf" for very large datasets
        "index_path": "vector_index.idx",
        "metadata_path": "vector_metadata.pkl"
    }
    
    logger.info("Starting optimized vector store creation...")
    logger.info(f"Configuration: {config}")
    
    # Estimate processing time
    try:
        with open(config["chunked_docs_path"], 'rb') as f:
            chunked_docs = pickle.load(f)
        
        time_estimate = estimate_processing_time(len(chunked_docs), config["batch_size"])
        print(f"\nTime Estimation:")
        print(f"Total chunks: {time_estimate['total_chunks']:,}")
        print(f"Estimated time: {time_estimate['estimated_minutes']:.1f} minutes ({time_estimate['estimated_hours']:.2f} hours)")
        print(f"Processing speed: {time_estimate['chunks_per_second']} chunks/second")
        print()
        
    except Exception as e:
        logger.warning(f"Could not estimate processing time: {e}")
    
    try:
        # Create vector store
        vector_store = create_optimized_vector_store(
            chunked_docs_path=config["chunked_docs_path"],
            model_name=config["model_name"],
            batch_size=config["batch_size"],
            index_type=config["index_type"]
        )
        
        # Save vector store
        vector_store.save_vector_store(
            index_path=config["index_path"],
            metadata_path=config["metadata_path"]
        )
        
        # Print statistics
        stats = vector_store.get_stats()
        print(f"\nVector Store Statistics:")
        print(f"Total vectors: {stats['total_vectors']:,}")
        print(f"Embedding dimension: {stats['embedding_dimension']}")
        print(f"Model: {stats['model_name']}")
        print(f"Index type: {stats['index_type']}")
        
        # Test search functionality
        test_vector_search(vector_store)
        
        logger.info("Optimized vector store creation completed successfully!")
        
        return vector_store
        
    except Exception as e:
        logger.error(f"Error creating vector store: {str(e)}")
        raise


if __name__ == "__main__":
    vector_store = main()


