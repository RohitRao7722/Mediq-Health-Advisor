"""
Data Ingestion Pipeline for Personalized Health Chatbot

This module converts mixed-format health data (CSV, PDF, TXT, JSON, HTML) 
into a uniform list of LangChain documents with clear content and metadata.
"""

from langchain_community.document_loaders import (
    CSVLoader, TextLoader, JSONLoader, PyPDFLoader, UnstructuredHTMLLoader
)
import os
import logging
from typing import List
from langchain.schema import Document

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_documents(data_dirs: List[str]) -> List[Document]:
    """
    Load documents from multiple directories with different file formats.
    
    Args:
        data_dirs: List of directory paths containing data files
        
    Returns:
        List of LangChain Document objects
    """
    documents = []
    total_files_processed = 0
    total_files_failed = 0
    
    for data_dir in data_dirs:
        if not os.path.exists(data_dir):
            logger.warning(f"Directory {data_dir} does not exist, skipping...")
            continue
            
        logger.info(f"Processing directory: {data_dir}")
        
        for fname in os.listdir(data_dir):
            fpath = os.path.join(data_dir, fname)
            
            # Skip directories
            if os.path.isdir(fpath):
                continue
                
            try:
                if fname.endswith(".csv"):
                    logger.info(f"Loading CSV: {fname}")
                    # Handle large CSV files that might cause memory issues
                    try:
                        docs = CSVLoader(fpath).load()
                        documents.extend(docs)
                        total_files_processed += 1
                    except Exception as csv_error:
                        logger.warning(f"CSVLoader failed for {fname}, trying alternative method: {str(csv_error)}")
                        # Try loading with pandas as fallback
                        try:
                            import pandas as pd
                            # Try different encodings
                            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                            df = None
                            
                            for encoding in encodings:
                                try:
                                    df = pd.read_csv(fpath, encoding=encoding, low_memory=False)
                                    logger.info(f"Successfully loaded {fname} with {encoding} encoding")
                                    break
                                except UnicodeDecodeError:
                                    continue
                            
                            if df is None:
                                raise Exception("Could not decode file with any supported encoding")
                            
                            # Convert to documents manually
                            for idx, row in df.iterrows():
                                content = "\n".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                                doc = Document(
                                    page_content=content,
                                    metadata={"source": fpath, "row": idx, "file_type": "csv"}
                                )
                                documents.append(doc)
                            total_files_processed += 1
                            logger.info(f"Successfully loaded {fname} using pandas fallback")
                        except Exception as pandas_error:
                            logger.error(f"Both CSVLoader and pandas failed for {fname}: {str(pandas_error)}")
                            total_files_failed += 1
                    
                elif fname.endswith(".txt"):
                    logger.info(f"Loading TXT: {fname}")
                    docs = TextLoader(fpath, encoding='utf-8').load()
                    documents.extend(docs)
                    total_files_processed += 1
                    
                elif fname.endswith(".json"):
                    logger.info(f"Loading JSON: {fname}")
                    docs = JSONLoader(fpath).load()
                    documents.extend(docs)
                    total_files_processed += 1
                    
                elif fname.endswith(".pdf"):
                    logger.info(f"Loading PDF: {fname}")
                    docs = PyPDFLoader(fpath).load()
                    documents.extend(docs)
                    total_files_processed += 1
                    
                elif fname.endswith(".html"):
                    logger.info(f"Loading HTML: {fname}")
                    docs = UnstructuredHTMLLoader(fpath).load()
                    documents.extend(docs)
                    total_files_processed += 1
                    
                else:
                    logger.info(f"Skipping unsupported file: {fname}")
                    
            except Exception as e:
                logger.error(f"Failed to load {fname}: {str(e)}")
                total_files_failed += 1
                continue
    
    logger.info(f"Data ingestion complete!")
    logger.info(f"Files processed successfully: {total_files_processed}")
    logger.info(f"Files failed: {total_files_failed}")
    logger.info(f"Total documents loaded: {len(documents)}")
    
    return documents


def inspect_documents(documents: List[Document], num_samples: int = 3) -> None:
    """
    Inspect a sample of loaded documents to verify structure and content.
    
    Args:
        documents: List of Document objects
        num_samples: Number of documents to inspect
    """
    print(f"\n{'='*80}")
    print(f"INSPECTING {min(num_samples, len(documents))} SAMPLE DOCUMENTS")
    print(f"{'='*80}")
    
    for i, doc in enumerate(documents[:num_samples]):
        print(f"\nDocument {i+1}:")
        print(f"Metadata: {doc.metadata}")
        print(f"Content preview (first 300 chars):")
        print(f"{doc.page_content[:300]}...")
        print(f"Content length: {len(doc.page_content)} characters")
        print("-" * 80)


def save_documents_summary(documents: List[Document], output_file: str = "documents_summary.txt") -> None:
    """
    Save a summary of all loaded documents for inspection.
    
    Args:
        documents: List of Document objects
        output_file: Output file path for the summary
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"DOCUMENTS LOADING SUMMARY\n")
        f.write(f"{'='*50}\n")
        f.write(f"Total documents loaded: {len(documents)}\n\n")
        
        # Group by source directory
        source_counts = {}
        for doc in documents:
            source = doc.metadata.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        f.write("Documents by source:\n")
        for source, count in source_counts.items():
            f.write(f"  {source}: {count} documents\n")
        
        f.write(f"\nSample documents:\n")
        f.write(f"{'='*30}\n")
        
        for i, doc in enumerate(documents[:5]):  # First 5 documents
            f.write(f"\nDocument {i+1}:\n")
            f.write(f"Source: {doc.metadata.get('source', 'unknown')}\n")
            f.write(f"Content length: {len(doc.page_content)} characters\n")
            f.write(f"Content preview:\n{doc.page_content[:500]}...\n")
            f.write("-" * 50 + "\n")


def main():
    """Main function to run the data ingestion pipeline."""
    
    # List the raw data folders to ingest
    data_dirs = [
        "data/raw/kaggle",
        "data/raw/NIH MedlinePlus Health Topics", 
        "data/raw/who",
    ]
    
    print("Starting data ingestion pipeline...")
    print(f"Target directories: {data_dirs}")
    
    # Load all documents
    documents = load_documents(data_dirs)
    
    # Inspect sample documents
    inspect_documents(documents, num_samples=3)
    
    # Save summary for inspection
    save_documents_summary(documents)
    print(f"\nDocuments summary saved to: documents_summary.txt")
    
    return documents


if __name__ == "__main__":
    docs = main()
