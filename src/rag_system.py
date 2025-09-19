"""
RAG (Retrieval-Augmented Generation) System for Health Chatbot

This module implements a complete RAG system that combines:
1. Vector search for relevant health information
2. Groq LLM integration for natural language responses
3. Health-focused prompting and safety features
"""

import os
import pickle
import faiss
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import logging
from datetime import datetime
import json

# Groq integration
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Warning: Groq not available. Install with: pip install groq")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthRAGSystem:
    """
    Complete RAG system for health chatbot using Groq LLM.
    """
    
    def __init__(self, 
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 index_path: str = "vector_index.idx",
                 metadata_path: str = "vector_metadata.pkl",
                 groq_api_key: Optional[str] = None,
                 groq_model: str = "llama-3.1-8b-instant"):
        """
        Initialize the RAG system.
        
        Args:
            model_name: Sentence transformer model name
            index_path: Path to FAISS index
            metadata_path: Path to metadata file
            groq_api_key: Groq API key (if None, will try to get from environment)
            groq_model: Groq model name
        """
        self.model_name = model_name
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.groq_model = groq_model
        
        # Initialize components
        self.embedder = None
        self.faiss_index = None
        self.metadata = []
        self.groq_client = None
        
        # Force CPU usage for embedding model
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        
        # Initialize Groq client
        self._setup_groq_client(groq_api_key)
        
    def _setup_groq_client(self, api_key: Optional[str] = None):
        """Setup Groq client."""
        if not GROQ_AVAILABLE:
            raise ImportError("Groq library not available. Install with: pip install groq")
        
        api_key = api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Groq API key not provided. Set GROQ_API_KEY environment variable or pass api_key parameter.")
        
        try:
            self.groq_client = Groq(api_key=api_key)
            logger.info(f"Groq client initialized with model: {self.groq_model}")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {str(e)}")
            raise
    
    def load_search_system(self):
        """Load the search system components."""
        logger.info("Loading RAG search system...")
        
        # Load embedding model
        logger.info(f"Loading embedding model: {self.model_name}")
        self.embedder = SentenceTransformer(self.model_name, device='cpu')
        
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
        
        logger.info(f"RAG system loaded successfully!")
        logger.info(f"Index vectors: {self.faiss_index.ntotal:,}")
        logger.info(f"Metadata entries: {len(self.metadata):,}")
        logger.info(f"Groq model: {self.groq_model}")
    
    def search_relevant_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using vector similarity.
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with metadata
        """
        if self.faiss_index is None:
            raise ValueError("Search system not loaded. Call load_search_system() first.")
        
        # Generate query embedding
        query_embedding = self.embedder.encode([query], convert_to_numpy=True)
        
        # Search in FAISS index
        scores, indices = self.faiss_index.search(query_embedding.astype('float32'), k)
        
        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata):
                results.append({
                    'score': float(score),
                    'metadata': self.metadata[idx],
                    'index': int(idx)
                })
        
        return results
    
    def create_health_prompt(self, query: str, relevant_docs: List[Dict[str, Any]]) -> str:
        """
        Create a health-focused prompt for the LLM.
        
        Args:
            query: User's health question
            relevant_docs: Retrieved relevant documents
            
        Returns:
            Formatted prompt for the LLM
        """
        # Medical disclaimer
        disclaimer = """
IMPORTANT MEDICAL DISCLAIMER:
- This is an AI assistant providing general health information
- This is NOT a substitute for professional medical advice, diagnosis, or treatment
- Always consult with qualified healthcare professionals for medical concerns
- In case of medical emergency, call emergency services immediately
- Do not delay seeking professional medical advice based on this information
"""
        
        # Format relevant documents
        context_parts = []
        for i, doc in enumerate(relevant_docs, 1):
            metadata = doc['metadata']
            source = metadata.get('source', 'Unknown')
            
            # Determine content type
            if 'ai-medical-chatbot.csv' in source:
                content_type = "Medical Q&A Database"
            elif 'medquad.csv' in source:
                content_type = "Medical Knowledge Base"
            elif 'NIH' in source:
                content_type = "NIH Health Information"
            elif 'who' in source:
                content_type = "WHO Health Guidelines"
            else:
                content_type = "Health Data"
            
            context_parts.append(f"[Source {i}: {content_type}]")
            context_parts.append(f"Relevance Score: {doc['score']:.3f}")
            context_parts.append(f"File: {os.path.basename(source)}")
            context_parts.append("---")
        
        context = "\n".join(context_parts)
        
        # Main prompt
        prompt = f"""{disclaimer}

You are a helpful AI health assistant. Based on the provided medical information, please answer the user's health question accurately and responsibly.

RELEVANT MEDICAL INFORMATION:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
1. Provide a clear, accurate answer based on the relevant information above
2. If the information is insufficient, clearly state this limitation
3. Always emphasize the importance of consulting healthcare professionals
4. For emergency symptoms, immediately advise seeking emergency medical care
5. Use clear, accessible language while maintaining medical accuracy
6. Include relevant precautions and when to seek medical attention

RESPONSE:"""
        
        return prompt
    
    def generate_response(self, query: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Generate a response using RAG system.
        
        Args:
            query: User's health question
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary containing response and metadata
        """
        if self.groq_client is None:
            raise ValueError("Groq client not initialized")
        
        try:
            # Search for relevant documents
            relevant_docs = self.search_relevant_documents(query, k=5)
            
            # Create prompt
            prompt = self.create_health_prompt(query, relevant_docs)
            
            # Generate response with Groq
            for attempt in range(max_retries):
                try:
                    response = self.groq_client.chat.completions.create(
                        model=self.groq_model,
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.3,  # Lower temperature for more consistent medical responses
                        max_tokens=1000,
                        top_p=0.9
                    )
                    
                    # Extract response content
                    response_text = response.choices[0].message.content
                    
                    # Calculate response metadata
                    response_metadata = {
                        'query': query,
                        'timestamp': datetime.now().isoformat(),
                        'model_used': self.groq_model,
                        'relevant_docs_count': len(relevant_docs),
                        'top_doc_score': relevant_docs[0]['score'] if relevant_docs else None,
                        'attempt': attempt + 1,
                        'response_length': len(response_text)
                    }
                    
                    return {
                        'response': response_text,
                        'metadata': response_metadata,
                        'relevant_docs': relevant_docs
                    }
                    
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                    continue
            
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            return {
                'response': "I apologize, but I'm experiencing technical difficulties. Please try again or consult a healthcare professional for immediate medical concerns.",
                'metadata': {
                    'query': query,
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e),
                    'model_used': self.groq_model
                },
                'relevant_docs': []
            }
    
    def chat(self, message: str) -> str:
        """
        Simple chat interface that returns just the response text.
        
        Args:
            message: User's message
            
        Returns:
            AI response text
        """
        result = self.generate_response(message)
        return result['response']
    
    def get_conversation_context(self, query: str) -> Dict[str, Any]:
        """
        Get detailed conversation context including sources and metadata.
        
        Args:
            query: User's health question
            
        Returns:
            Detailed response with sources and metadata
        """
        return self.generate_response(query)


def main():
    """Main function to test the RAG system."""
    
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
        print("Error: GROQ_API_KEY environment variable not set.")
        print("Please set your Groq API key:")
        print("export GROQ_API_KEY='your-api-key-here'")
        return
    
    try:
        # Initialize RAG system
        rag_system = HealthRAGSystem(**config, groq_api_key=groq_api_key)
        
        # Load search system
        rag_system.load_search_system()
        
        print("="*80)
        print("HEALTH CHATBOT RAG SYSTEM")
        print("="*80)
        print("System loaded successfully!")
        print(f"Model: {config['groq_model']}")
        print(f"Vector database: {rag_system.faiss_index.ntotal:,} documents")
        print("\nEnter health questions (type 'quit' to exit):")
        print("-" * 80)
        
        # Interactive chat loop
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! Stay healthy!")
                    break
                
                if not user_input:
                    print("Please enter a health question.")
                    continue
                
                print("\nAI: ", end="", flush=True)
                response = rag_system.chat(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! Stay healthy!")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {str(e)}")
        raise


if __name__ == "__main__":
    main()

