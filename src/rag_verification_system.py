"""
RAG Verification System for Health Chatbot

This module provides comprehensive verification mechanisms to ensure that
responses are generated from the actual data sources and not LLM hallucinations.
"""

import os
import re
import json
import pickle
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SourceVerification:
    """Data class for source verification results."""
    source_id: str
    source_file: str
    content_hash: str
    similarity_score: float
    exact_matches: List[str]
    semantic_overlap: float
    is_verified: bool
    verification_confidence: float

@dataclass
class ResponseVerification:
    """Data class for complete response verification."""
    query: str
    response: str
    sources_used: List[SourceVerification]
    total_verification_score: float
    is_grounded: bool
    hallucination_risk: str  # "LOW", "MEDIUM", "HIGH"
    verification_details: Dict[str, Any]

class RAGVerificationSystem:
    """
    Comprehensive system to verify RAG responses against source data.
    """
    
    def __init__(self, 
                 metadata_path: str = "vector_metadata.pkl",
                 embedder_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the verification system.
        
        Args:
            metadata_path: Path to the metadata file
            embedder_model: Sentence transformer model for semantic similarity
        """
        self.metadata_path = metadata_path
        self.embedder = SentenceTransformer(embedder_model, device='cpu')
        self.metadata = []
        self.source_content_cache = {}
        
        # Load metadata
        self._load_metadata()
        
        # Verification thresholds
        self.EXACT_MATCH_THRESHOLD = 0.8  # For exact phrase matching
        self.SEMANTIC_SIMILARITY_THRESHOLD = 0.7  # For semantic similarity
        self.GROUNDING_THRESHOLD = 0.6  # Overall grounding threshold
        
    def _load_metadata(self):
        """Load metadata from pickle file."""
        try:
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            logger.info(f"Loaded {len(self.metadata)} metadata entries")
        except Exception as e:
            logger.error(f"Failed to load metadata: {str(e)}")
            raise
    
    def _get_source_content(self, source_path: str) -> str:
        """
        Get content from source file with caching.
        
        Args:
            source_path: Path to source file
            
        Returns:
            Content of the source file
        """
        if source_path in self.source_content_cache:
            return self.source_content_cache[source_path]
        
        try:
            if os.path.exists(source_path):
                with open(source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.source_content_cache[source_path] = content
                return content
            else:
                logger.warning(f"Source file not found: {source_path}")
                return ""
        except Exception as e:
            logger.error(f"Error reading source file {source_path}: {str(e)}")
            return ""
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate hash of content for verification."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _find_exact_matches(self, response: str, source_content: str) -> List[str]:
        """
        Find exact phrase matches between response and source.
        
        Args:
            response: Generated response
            source_content: Source document content
            
        Returns:
            List of exact matching phrases
        """
        # Clean and normalize text
        response_clean = re.sub(r'[^\w\s]', ' ', response.lower())
        source_clean = re.sub(r'[^\w\s]', ' ', source_content.lower())
        
        # Find phrases of 3+ words that appear in both
        response_words = response_clean.split()
        source_words = source_clean.split()
        
        exact_matches = []
        
        # Check for 3-5 word phrases
        for phrase_length in range(3, 6):
            for i in range(len(response_words) - phrase_length + 1):
                phrase = ' '.join(response_words[i:i + phrase_length])
                if phrase in ' '.join(source_words):
                    exact_matches.append(phrase)
        
        return list(set(exact_matches))  # Remove duplicates
    
    def _calculate_semantic_similarity(self, response: str, source_content: str) -> float:
        """
        Calculate semantic similarity between response and source.
        
        Args:
            response: Generated response
            source_content: Source document content
            
        Returns:
            Semantic similarity score (0-1)
        """
        try:
            # Encode texts
            response_embedding = self.embedder.encode([response])
            source_embedding = self.embedder.encode([source_content])
            
            # Calculate cosine similarity
            similarity = np.dot(response_embedding[0], source_embedding[0]) / (
                np.linalg.norm(response_embedding[0]) * np.linalg.norm(source_embedding[0])
            )
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {str(e)}")
            return 0.0
    
    def verify_source_grounding(self, response: str, source_metadata: Dict[str, Any]) -> SourceVerification:
        """
        Verify if response is grounded in a specific source.
        
        Args:
            response: Generated response text
            source_metadata: Metadata for the source document
            
        Returns:
            SourceVerification object with verification results
        """
        source_path = source_metadata.get('source', '')
        source_content = self._get_source_content(source_path)
        
        if not source_content:
            return SourceVerification(
                source_id=str(source_metadata.get('id', 'unknown')),
                source_file=os.path.basename(source_path),
                content_hash=self._calculate_content_hash(""),
                similarity_score=0.0,
                exact_matches=[],
                semantic_overlap=0.0,
                is_verified=False,
                verification_confidence=0.0
            )
        
        # Find exact matches
        exact_matches = self._find_exact_matches(response, source_content)
        
        # Calculate semantic similarity
        semantic_similarity = self._calculate_semantic_similarity(response, source_content)
        
        # Calculate verification confidence
        exact_match_score = min(len(exact_matches) * 0.2, 1.0)  # Cap at 1.0
        verification_confidence = (exact_match_score * 0.4) + (semantic_similarity * 0.6)
        
        # Determine if verified
        is_verified = (
            len(exact_matches) > 0 and 
            semantic_similarity > self.SEMANTIC_SIMILARITY_THRESHOLD
        ) or verification_confidence > self.GROUNDING_THRESHOLD
        
        return SourceVerification(
            source_id=str(source_metadata.get('id', 'unknown')),
            source_file=os.path.basename(source_path),
            content_hash=self._calculate_content_hash(source_content),
            similarity_score=semantic_similarity,
            exact_matches=exact_matches,
            semantic_overlap=verification_confidence,
            is_verified=is_verified,
            verification_confidence=verification_confidence
        )
    
    def verify_response(self, 
                       query: str, 
                       response: str, 
                       relevant_docs: List[Dict[str, Any]]) -> ResponseVerification:
        """
        Comprehensive verification of RAG response.
        
        Args:
            query: Original user query
            response: Generated response
            relevant_docs: List of relevant documents used
            
        Returns:
            ResponseVerification object with complete verification results
        """
        source_verifications = []
        
        # Verify each source
        for doc in relevant_docs:
            source_verification = self.verify_source_grounding(response, doc['metadata'])
            source_verifications.append(source_verification)
        
        # Calculate overall verification score
        if source_verifications:
            total_score = sum(sv.verification_confidence for sv in source_verifications) / len(source_verifications)
            verified_sources = sum(1 for sv in source_verifications if sv.is_verified)
            verification_ratio = verified_sources / len(source_verifications)
        else:
            total_score = 0.0
            verification_ratio = 0.0
        
        # Determine grounding status
        is_grounded = total_score > self.GROUNDING_THRESHOLD and verification_ratio > 0.3
        
        # Determine hallucination risk
        if total_score > 0.8 and verification_ratio > 0.6:
            hallucination_risk = "LOW"
        elif total_score > 0.5 and verification_ratio > 0.3:
            hallucination_risk = "MEDIUM"
        else:
            hallucination_risk = "HIGH"
        
        # Collect verification details
        verification_details = {
            'total_sources': len(relevant_docs),
            'verified_sources': sum(1 for sv in source_verifications if sv.is_verified),
            'average_similarity': np.mean([sv.similarity_score for sv in source_verifications]) if source_verifications else 0.0,
            'total_exact_matches': sum(len(sv.exact_matches) for sv in source_verifications),
            'verification_timestamp': datetime.now().isoformat(),
            'thresholds_used': {
                'exact_match': self.EXACT_MATCH_THRESHOLD,
                'semantic_similarity': self.SEMANTIC_SIMILARITY_THRESHOLD,
                'grounding': self.GROUNDING_THRESHOLD
            }
        }
        
        return ResponseVerification(
            query=query,
            response=response,
            sources_used=source_verifications,
            total_verification_score=total_score,
            is_grounded=is_grounded,
            hallucination_risk=hallucination_risk,
            verification_details=verification_details
        )
    
    def generate_verification_report(self, verification: ResponseVerification) -> str:
        """
        Generate a human-readable verification report.
        
        Args:
            verification: ResponseVerification object
            
        Returns:
            Formatted verification report
        """
        report = f"""
=== RAG RESPONSE VERIFICATION REPORT ===

Query: {verification.query}

Response Grounding Status: {'✅ GROUNDED' if verification.is_grounded else '❌ NOT GROUNDED'}
Hallucination Risk: {verification.hallucination_risk}
Overall Verification Score: {verification.total_verification_score:.3f}

Source Analysis:
"""
        
        for i, source in enumerate(verification.sources_used, 1):
            status = "✅ VERIFIED" if source.is_verified else "❌ NOT VERIFIED"
            report += f"""
Source {i}: {source.source_file}
  Status: {status}
  Similarity Score: {source.similarity_score:.3f}
  Exact Matches: {len(source.exact_matches)} phrases
  Verification Confidence: {source.verification_confidence:.3f}
  Sample Matches: {', '.join(source.exact_matches[:3])}
"""
        
        report += f"""
Summary Statistics:
- Total Sources Analyzed: {verification.verification_details['total_sources']}
- Sources Verified: {verification.verification_details['verified_sources']}
- Average Similarity: {verification.verification_details['average_similarity']:.3f}
- Total Exact Matches: {verification.verification_details['total_exact_matches']}

Verification completed at: {verification.verification_details['verification_timestamp']}
"""
        
        return report
    
    def create_verification_api_response(self, verification: ResponseVerification) -> Dict[str, Any]:
        """
        Create API-friendly verification response.
        
        Args:
            verification: ResponseVerification object
            
        Returns:
            Dictionary suitable for API response
        """
        return {
            'verification': {
                'is_grounded': verification.is_grounded,
                'hallucination_risk': verification.hallucination_risk,
                'verification_score': verification.total_verification_score,
                'sources_verified': verification.verification_details['verified_sources'],
                'total_sources': verification.verification_details['total_sources'],
                'exact_matches_found': verification.verification_details['total_exact_matches']
            },
            'source_details': [
                {
                    'source_file': source.source_file,
                    'is_verified': source.is_verified,
                    'similarity_score': source.similarity_score,
                    'exact_matches_count': len(source.exact_matches),
                    'sample_matches': source.exact_matches[:3],
                    'confidence': source.verification_confidence
                }
                for source in verification.sources_used
            ],
            'verification_metadata': verification.verification_details
        }


def main():
    """Test the verification system."""
    print("Testing RAG Verification System...")
    
    # Initialize verification system
    verifier = RAGVerificationSystem()
    
    # Test with sample data
    sample_query = "What are the symptoms of diabetes?"
    sample_response = "Common symptoms of diabetes include increased thirst, frequent urination, and unexplained weight loss."
    sample_docs = [
        {
            'metadata': {
                'source': 'data/raw/NIH MedlinePlus Health Topics/diabetes.txt',
                'id': 'doc_123'
            },
            'score': 0.85
        }
    ]
    
    # Verify response
    verification = verifier.verify_response(sample_query, sample_response, sample_docs)
    
    # Generate report
    report = verifier.generate_verification_report(verification)
    print(report)
    
    # Generate API response
    api_response = verifier.create_verification_api_response(verification)
    print("\nAPI Response:")
    print(json.dumps(api_response, indent=2))


if __name__ == "__main__":
    main()
