"""
Document Chunking and Preprocessing for Personalized Health Chatbot

This module handles splitting documents into optimal chunks for embedding and retrieval,
preserving metadata and ensuring logical text boundaries.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List
import logging
import pickle
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def chunk_documents(documents: List[Document], 
                   chunk_size: int = 2000, 
                   chunk_overlap: int = 200,
                   separators: List[str] = None) -> List[Document]:
    """
    Split documents into chunks using RecursiveCharacterTextSplitter.
    
    Args:
        documents: List of Document objects to chunk
        chunk_size: Target size for each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks
        separators: Custom separators for splitting (optional)
        
    Returns:
        List of chunked Document objects
    """
    if separators is None:
        # Default separators optimized for health/medical content
        separators = [
            "\n\n",  # Paragraph breaks
            "\n",    # Line breaks
            ". ",    # Sentence endings
            "! ",    # Exclamation sentences
            "? ",    # Question sentences
            "; ",    # Semicolon breaks
            ", ",    # Comma breaks
            " ",     # Word breaks
            ""       # Character breaks (fallback)
        ]
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
        length_function=len,
        is_separator_regex=False
    )
    
    chunked_docs = []
    total_original_docs = len(documents)
    
    logger.info(f"Starting chunking process for {total_original_docs} documents...")
    logger.info(f"Chunk size: {chunk_size} characters, Overlap: {chunk_overlap} characters")
    
    for i, doc in enumerate(documents):
        try:
            # Split the document content
            chunks = splitter.split_text(doc.page_content)
            
            # Create Document objects for each chunk
            for chunk_idx, chunk_text in enumerate(chunks):
                # Preserve original metadata and add chunk-specific info
                chunk_metadata = doc.metadata.copy()
                chunk_metadata.update({
                    'chunk_index': chunk_idx,
                    'total_chunks': len(chunks),
                    'chunk_size': len(chunk_text),
                    'original_doc_index': i
                })
                
                chunked_doc = Document(
                    page_content=chunk_text,
                    metadata=chunk_metadata
                )
                chunked_docs.append(chunked_doc)
            
            if (i + 1) % 1000 == 0:
                logger.info(f"Processed {i + 1}/{total_original_docs} documents...")
                
        except Exception as e:
            logger.error(f"Error chunking document {i}: {str(e)}")
            # Add the original document as a single chunk if chunking fails
            chunked_docs.append(doc)
    
    logger.info(f"Chunking complete! Created {len(chunked_docs)} chunks from {total_original_docs} documents")
    return chunked_docs


def inspect_chunks(chunked_docs: List[Document], 
                  num_samples: int = 5,
                  show_metadata: bool = True) -> None:
    """
    Inspect sample chunks to verify quality and metadata preservation.
    
    Args:
        chunked_docs: List of chunked Document objects
        num_samples: Number of chunks to inspect
        show_metadata: Whether to display metadata
    """
    print(f"\n{'='*80}")
    print(f"CHUNK INSPECTION - {min(num_samples, len(chunked_docs))} SAMPLE CHUNKS")
    print(f"{'='*80}")
    
    for i, chunk in enumerate(chunked_docs[:num_samples]):
        print(f"\nChunk {i+1}:")
        print(f"Content length: {len(chunk.page_content)} characters")
        print(f"Content preview (first 300 chars):")
        print(f"{chunk.page_content[:300]}...")
        
        if show_metadata:
            print(f"Metadata: {chunk.metadata}")
        
        print("-" * 80)


def analyze_chunk_statistics(chunked_docs: List[Document]) -> dict:
    """
    Analyze chunk statistics for optimization insights.
    
    Args:
        chunked_docs: List of chunked Document objects
        
    Returns:
        Dictionary with chunk statistics
    """
    chunk_sizes = [len(chunk.page_content) for chunk in chunked_docs]
    
    stats = {
        'total_chunks': len(chunked_docs),
        'avg_chunk_size': sum(chunk_sizes) / len(chunk_sizes),
        'min_chunk_size': min(chunk_sizes),
        'max_chunk_size': max(chunk_sizes),
        'chunks_by_source': {},
        'chunks_per_doc': {}
    }
    
    # Analyze chunks by source
    for chunk in chunked_docs:
        source = chunk.metadata.get('source', 'unknown')
        stats['chunks_by_source'][source] = stats['chunks_by_source'].get(source, 0) + 1
        
        # Track chunks per original document
        orig_doc_idx = chunk.metadata.get('original_doc_index', 'unknown')
        if orig_doc_idx != 'unknown':
            stats['chunks_per_doc'][orig_doc_idx] = stats['chunks_per_doc'].get(orig_doc_idx, 0) + 1
    
    return stats


def save_chunked_documents(chunked_docs: List[Document], 
                          output_file: str = "chunked_documents.pkl") -> None:
    """
    Save chunked documents to disk for later use.
    
    Args:
        chunked_docs: List of chunked Document objects
        output_file: Output file path
    """
    try:
        with open(output_file, 'wb') as f:
            pickle.dump(chunked_docs, f)
        logger.info(f"Saved {len(chunked_docs)} chunked documents to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save chunked documents: {str(e)}")


def load_chunked_documents(input_file: str = "chunked_documents.pkl") -> List[Document]:
    """
    Load chunked documents from disk.
    
    Args:
        input_file: Input file path
        
    Returns:
        List of chunked Document objects
    """
    try:
        with open(input_file, 'rb') as f:
            chunked_docs = pickle.load(f)
        logger.info(f"Loaded {len(chunked_docs)} chunked documents from {input_file}")
        return chunked_docs
    except Exception as e:
        logger.error(f"Failed to load chunked documents: {str(e)}")
        return []


def optimize_chunking_parameters(documents: List[Document], 
                                test_sizes: List[int] = [1000, 1500, 2000, 2500],
                                test_overlaps: List[int] = [100, 150, 200, 250]) -> dict:
    """
    Test different chunking parameters to find optimal settings.
    
    Args:
        documents: Sample of documents to test with
        test_sizes: List of chunk sizes to test
        test_overlaps: List of overlap sizes to test
        
    Returns:
        Dictionary with optimization results
    """
    logger.info("Testing chunking parameters...")
    results = {}
    
    # Use a sample of documents for testing (first 100)
    test_docs = documents[:100]
    
    for size in test_sizes:
        for overlap in test_overlaps:
            if overlap >= size:
                continue  # Skip invalid combinations
                
            try:
                chunked = chunk_documents(test_docs, chunk_size=size, chunk_overlap=overlap)
                stats = analyze_chunk_statistics(chunked)
                
                key = f"size_{size}_overlap_{overlap}"
                results[key] = {
                    'chunk_size': size,
                    'chunk_overlap': overlap,
                    'total_chunks': stats['total_chunks'],
                    'avg_chunk_size': stats['avg_chunk_size'],
                    'efficiency': len(test_docs) / stats['total_chunks']  # Lower is better
                }
                
            except Exception as e:
                logger.warning(f"Failed to test size {size}, overlap {overlap}: {str(e)}")
    
    # Find optimal parameters
    best_efficiency = min(results.values(), key=lambda x: x['efficiency'])
    logger.info(f"Optimal parameters found: {best_efficiency}")
    
    return results


def main():
    """Main function to run the chunking pipeline."""
    from data_ingestion import load_documents
    
    # Load documents
    data_dirs = [
        "data/raw/kaggle",
        "data/raw/NIH MedlinePlus Health Topics", 
        "data/raw/who",
    ]
    
    logger.info("Loading documents for chunking...")
    documents = load_documents(data_dirs)
    
    # Chunk documents with optimized parameters
    logger.info("Starting document chunking...")
    chunked_docs = chunk_documents(
        documents, 
        chunk_size=2000,  # ~500-1000 tokens
        chunk_overlap=200  # ~50-100 tokens
    )
    
    # Inspect chunks
    inspect_chunks(chunked_docs, num_samples=3)
    
    # Analyze statistics
    stats = analyze_chunk_statistics(chunked_docs)
    print(f"\nChunk Statistics:")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Average chunk size: {stats['avg_chunk_size']:.0f} characters")
    print(f"Min chunk size: {stats['min_chunk_size']} characters")
    print(f"Max chunk size: {stats['max_chunk_size']} characters")
    
    # Save chunked documents
    save_chunked_documents(chunked_docs)
    
    return chunked_docs


if __name__ == "__main__":
    chunked_docs = main()
