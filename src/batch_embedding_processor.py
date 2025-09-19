"""
Batch Embedding Processor for Large Datasets

This script processes chunks in batches to avoid memory issues and allow
for progress monitoring and recovery.
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
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BatchEmbeddingProcessor:
    """
    Processes embeddings in batches for large datasets.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 batch_size: int = 128, chunk_batch_size: int = 50000):
        """
        Initialize the batch processor.
        
        Args:
            model_name: Sentence transformer model name
            batch_size: Batch size for embedding generation
            chunk_batch_size: Number of chunks to process in each batch
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self.chunk_batch_size = chunk_batch_size
        self.model = None
        self.faiss_index = None
        self.metadata = []
        self.embedding_dim = None
        
        # Force CPU usage
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        
    def load_model(self):
        """Load the sentence transformer model."""
        if self.model is None:
            logger.info(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device='cpu')
            
            # Optimize for CPU
            import torch
            torch.set_num_threads(4)
            
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")
    
    def process_batch(self, chunked_docs: List, batch_num: int, total_batches: int) -> Tuple[np.ndarray, List]:
        """
        Process a batch of chunks.
        
        Args:
            chunked_docs: List of chunked documents
            batch_num: Current batch number
            total_batches: Total number of batches
            
        Returns:
            Tuple of (embeddings, metadata)
        """
        logger.info(f"Processing batch {batch_num}/{total_batches}")
        
        # Extract texts and metadata
        texts = [doc.page_content for doc in chunked_docs]
        metadata = [doc.metadata for doc in chunked_docs]
        
        # Generate embeddings
        start_time = time.time()
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        end_time = time.time()
        
        processing_time = end_time - start_time
        logger.info(f"Batch {batch_num} processed in {processing_time:.2f} seconds")
        logger.info(f"Processing speed: {len(chunked_docs)/processing_time:.2f} chunks/second")
        
        return embeddings, metadata
    
    def create_faiss_index(self, embedding_dim: int):
        """Create a new FAISS index."""
        logger.info("Creating new FAISS index")
        self.faiss_index = faiss.IndexFlatL2(embedding_dim)
        self.embedding_dim = embedding_dim
    
    def add_to_index(self, embeddings: np.ndarray):
        """Add embeddings to the FAISS index."""
        if self.faiss_index is None:
            self.create_faiss_index(embeddings.shape[1])
        
        self.faiss_index.add(embeddings.astype('float32'))
        logger.info(f"Added {len(embeddings)} vectors to index. Total: {self.faiss_index.ntotal}")
    
    def save_checkpoint(self, checkpoint_path: str = "checkpoint"):
        """Save current progress as checkpoint."""
        if not os.path.exists(checkpoint_path):
            os.makedirs(checkpoint_path)
        
        # Save FAISS index
        faiss.write_index(self.faiss_index, os.path.join(checkpoint_path, "vector_index.idx"))
        
        # Save metadata
        with open(os.path.join(checkpoint_path, "vector_metadata.pkl"), 'wb') as f:
            pickle.dump(self.metadata, f)
        
        # Save processing state
        state = {
            "processed_chunks": len(self.metadata),
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "timestamp": time.time()
        }
        
        with open(os.path.join(checkpoint_path, "processing_state.pkl"), 'wb') as f:
            pickle.dump(state, f)
        
        logger.info(f"Checkpoint saved to {checkpoint_path}")
    
    def load_checkpoint(self, checkpoint_path: str = "checkpoint"):
        """Load progress from checkpoint."""
        if not os.path.exists(checkpoint_path):
            logger.info("No checkpoint found, starting fresh")
            return False
        
        try:
            # Load FAISS index
            self.faiss_index = faiss.read_index(os.path.join(checkpoint_path, "vector_index.idx"))
            
            # Load metadata
            with open(os.path.join(checkpoint_path, "vector_metadata.pkl"), 'rb') as f:
                self.metadata = pickle.load(f)
            
            # Load state
            with open(os.path.join(checkpoint_path, "processing_state.pkl"), 'rb') as f:
                state = pickle.load(f)
            
            logger.info(f"Checkpoint loaded. Processed chunks: {len(self.metadata)}")
            logger.info(f"Index vectors: {self.faiss_index.ntotal}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}")
            return False
    
    def process_all_batches(self, chunked_docs_path: str = "chunked_documents.pkl",
                           checkpoint_path: str = "checkpoint",
                           resume: bool = True):
        """
        Process all chunks in batches.
        
        Args:
            chunked_docs_path: Path to chunked documents
            checkpoint_path: Path to save checkpoints
            resume: Whether to resume from checkpoint
        """
        # Load chunked documents
        logger.info(f"Loading chunked documents from {chunked_docs_path}")
        with open(chunked_docs_path, 'rb') as f:
            chunked_docs = pickle.load(f)
        
        total_chunks = len(chunked_docs)
        logger.info(f"Total chunks to process: {total_chunks:,}")
        
        # Calculate batches
        total_batches = (total_chunks + self.chunk_batch_size - 1) // self.chunk_batch_size
        logger.info(f"Processing in {total_batches} batches of {self.chunk_batch_size} chunks each")
        
        # Load model
        self.load_model()
        
        # Try to resume from checkpoint
        start_batch = 0
        if resume and self.load_checkpoint(checkpoint_path):
            start_batch = len(self.metadata) // self.chunk_batch_size
            logger.info(f"Resuming from batch {start_batch + 1}")
        
        # Process batches
        start_time = time.time()
        
        for batch_num in range(start_batch, total_batches):
            batch_start = batch_num * self.chunk_batch_size
            batch_end = min((batch_num + 1) * self.chunk_batch_size, total_chunks)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing batch {batch_num + 1}/{total_batches}")
            logger.info(f"Chunks {batch_start:,} to {batch_end:,}")
            logger.info(f"{'='*60}")
            
            # Get batch data
            batch_docs = chunked_docs[batch_start:batch_end]
            
            # Process batch
            embeddings, metadata = self.process_batch(batch_docs, batch_num + 1, total_batches)
            
            # Add to index
            self.add_to_index(embeddings)
            self.metadata.extend(metadata)
            
            # Save checkpoint every batch
            self.save_checkpoint(checkpoint_path)
            
            # Calculate progress
            processed_chunks = len(self.metadata)
            progress = (processed_chunks / total_chunks) * 100
            elapsed_time = time.time() - start_time
            estimated_total_time = (elapsed_time / processed_chunks) * total_chunks
            remaining_time = estimated_total_time - elapsed_time
            
            logger.info(f"Progress: {processed_chunks:,}/{total_chunks:,} ({progress:.1f}%)")
            logger.info(f"Elapsed time: {elapsed_time/60:.1f} minutes")
            logger.info(f"Estimated remaining time: {remaining_time/60:.1f} minutes")
        
        # Final save
        self.save_final_results()
        
        total_time = time.time() - start_time
        logger.info(f"\n{'='*60}")
        logger.info("PROCESSING COMPLETE!")
        logger.info(f"{'='*60}")
        logger.info(f"Total chunks processed: {len(self.metadata):,}")
        logger.info(f"Total time: {total_time/60:.1f} minutes")
        logger.info(f"Average speed: {len(self.metadata)/total_time:.2f} chunks/second")
        logger.info(f"Final index size: {self.faiss_index.ntotal:,} vectors")
    
    def save_final_results(self, index_path: str = "vector_index.idx",
                          metadata_path: str = "vector_metadata.pkl"):
        """Save final results."""
        logger.info("Saving final results...")
        
        # Save FAISS index
        faiss.write_index(self.faiss_index, index_path)
        logger.info(f"FAISS index saved to {index_path}")
        
        # Save metadata
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        logger.info(f"Metadata saved to {metadata_path}")
        
        # Clean up checkpoint directory
        if os.path.exists("checkpoint"):
            shutil.rmtree("checkpoint")
            logger.info("Checkpoint directory cleaned up")
    
    def test_search(self, query: str, k: int = 5):
        """Test search functionality."""
        if self.faiss_index is None:
            logger.error("No index available for search")
            return
        
        logger.info(f"Testing search for: '{query}'")
        
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search
        start_time = time.time()
        scores, indices = self.faiss_index.search(query_embedding.astype('float32'), k)
        search_time = time.time() - start_time
        
        logger.info(f"Search completed in {search_time:.4f} seconds")
        
        # Display results
        for i, (score, idx) in enumerate(zip(scores[0], indices[0]), 1):
            if idx < len(self.metadata):
                metadata = self.metadata[idx]
                print(f"\nResult {i} (Score: {score:.4f}):")
                print(f"  Source: {metadata.get('source', 'Unknown')}")
                print(f"  Chunk: {metadata.get('chunk_index', 'N/A')}/{metadata.get('total_chunks', 'N/A')}")


def main():
    """Main function to run batch processing."""
    
    # Configuration
    config = {
        "chunked_docs_path": "chunked_documents.pkl",
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "batch_size": 128,
        "chunk_batch_size": 50000,  # Process 50K chunks at a time
        "checkpoint_path": "checkpoint",
        "resume": True
    }
    
    logger.info("Starting batch embedding processing...")
    logger.info(f"Configuration: {config}")
    
    # Create processor
    processor = BatchEmbeddingProcessor(
        model_name=config["model_name"],
        batch_size=config["batch_size"],
        chunk_batch_size=config["chunk_batch_size"]
    )
    
    try:
        # Process all batches
        processor.process_all_batches(
            chunked_docs_path=config["chunked_docs_path"],
            checkpoint_path=config["checkpoint_path"],
            resume=config["resume"]
        )
        
        # Test search functionality
        logger.info("\nTesting search functionality...")
        test_queries = [
            "What are the symptoms of diabetes?",
            "How to treat depression?",
            "Blood pressure medication"
        ]
        
        for query in test_queries:
            processor.test_search(query, k=3)
        
        logger.info("Batch processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        raise


if __name__ == "__main__":
    main()


