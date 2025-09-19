"""
Embedding Generation and Vector Store for Personalized Health Chatbot

This module generates embeddings for chunked documents and stores them in a FAISS vector index
for ultra-fast similarity search and retrieval.
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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthVectorStore:
    """
    A vector store class for health-related document embeddings with FAISS backend.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
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
        """Load the sentence transformer model."""
        logger.info(f"Loading embedding model: {self.model_name}")
        self.embedder = SentenceTransformer(self.model_name)
        self.embedding_dim = self.embedder.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")
        
    def generate_embeddings(self, chunked_docs: List, 
                           batch_size: int = 512,
                           show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for all chunked documents.
        
        Args:
            chunked_docs: List of chunked Document objects
            batch_size: Batch size for embedding generation
            show_progress: Whether to show progress bar
            
        Returns:
            numpy array of embeddings
        """
        if self.embedder is None:
            self.load_embedding_model()
            
        logger.info(f"Generating embeddings for {len(chunked_docs)} chunks...")
        
        # Extract text content
        texts = [doc.page_content for doc in chunked_docs]
        
        # Generate embeddings with progress bar
        start_time = time.time()
        embeddings = self.embedder.encode(
            texts, 
            show_progress_bar=show_progress, 
            batch_size=batch_size,
            convert_to_numpy=True
        )
        
        end_time = time.time()
        logger.info(f"Embeddings generated in {end_time - start_time:.2f} seconds")
        logger.info(f"Embedding shape: {embeddings.shape}")
        
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
        query_embedding = self.embedder.encode([query])
        
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


def create_vector_store(chunked_docs_path: str = "chunked_documents.pkl",
                       model_name: str = "all-MiniLM-L6-v2",
                       batch_size: int = 512,
                       index_type: str = "flat") -> HealthVectorStore:
    """
    Create a complete vector store from chunked documents.
    
    Args:
        chunked_docs_path: Path to chunked documents pickle file
        model_name: Sentence transformer model name
        batch_size: Batch size for embedding generation
        index_type: Type of FAISS index
        
    Returns:
        HealthVectorStore instance
    """
    # Load chunked documents
    logger.info(f"Loading chunked documents from {chunked_docs_path}")
    with open(chunked_docs_path, 'rb') as f:
        chunked_docs = pickle.load(f)
    
    logger.info(f"Loaded {len(chunked_docs)} chunked documents")
    
    # Create vector store
    vector_store = HealthVectorStore(model_name=model_name)
    
    # Generate embeddings
    embeddings = vector_store.generate_embeddings(
        chunked_docs, 
        batch_size=batch_size
    )
    
    # Store metadata
    vector_store.metadata = [doc.metadata for doc in chunked_docs]
    
    # Create FAISS index
    vector_store.create_faiss_index(embeddings, index_type=index_type)
    
    return vector_store


def test_vector_search(vector_store: HealthVectorStore, 
                      test_queries: List[str] = None) -> None:
    """
    Test the vector search functionality with sample queries.
    
    Args:
        vector_store: HealthVectorStore instance
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
    print("VECTOR SEARCH TEST RESULTS")
    print(f"{'='*80}")
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 50)
        
        try:
            results = vector_store.search(query, k=3)
            
            for i, (score, metadata) in enumerate(results, 1):
                print(f"Result {i} (Score: {score:.4f}):")
                print(f"  Source: {metadata.get('source', 'Unknown')}")
                print(f"  Chunk: {metadata.get('chunk_index', 'N/A')}/{metadata.get('total_chunks', 'N/A')}")
                print(f"  Size: {metadata.get('chunk_size', 'N/A')} chars")
                print()
                
        except Exception as e:
            print(f"Error searching for '{query}': {str(e)}")


def main():
    """Main function to create and test the vector store."""
    
    # Configuration
    config = {
        "chunked_docs_path": "chunked_documents.pkl",
        "model_name": "all-MiniLM-L6-v2",  # Fast and efficient model
        "batch_size": 512,  # Adjust based on available memory
        "index_type": "flat",  # Use "ivf" for very large datasets
        "index_path": "vector_index.idx",
        "metadata_path": "vector_metadata.pkl"
    }
    
    logger.info("Starting vector store creation...")
    logger.info(f"Configuration: {config}")
    
    try:
        # Create vector store
        vector_store = create_vector_store(
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
        
        logger.info("Vector store creation completed successfully!")
        
        return vector_store
        
    except Exception as e:
        logger.error(f"Error creating vector store: {str(e)}")
        raise


if __name__ == "__main__":
    vector_store = main()


