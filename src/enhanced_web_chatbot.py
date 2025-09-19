"""
Enhanced Web-based Health Chatbot with Full API Support

This enhanced version provides all the API endpoints needed for the modern frontend,
including streaming responses, feedback, and comprehensive error handling.
"""

import os
import sys
import logging
import json
import time
import re
from datetime import datetime
from typing import Dict, Any, Optional, Generator
from flask import Flask, render_template, request, jsonify, Response, stream_with_context, g
from flask_cors import CORS
import threading
from contextlib import contextmanager
import html

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_system import HealthRAGSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global RAG system instance
rag_system = None
system_info = {}

def initialize_rag_system():
    """Initialize the RAG system."""
    global rag_system, system_info
    
    if rag_system is not None:
        return rag_system
    
    try:
        # Configuration
        config = {
            "model_name": "sentence-transformers/all-MiniLM-L6-v2",
            "index_path": "vector_index.idx",
            "metadata_path": "vector_metadata.pkl",
            "groq_model": "llama-3.1-8b-instant"
        }
        
        # Get Groq API key
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        # Initialize RAG system
        rag_system = HealthRAGSystem(**config, groq_api_key=groq_api_key)
        rag_system.load_search_system()
        
        # Store system info
        system_info = {
            "model": config["groq_model"],
            "vectors": rag_system.faiss_index.ntotal,
            "embedding_model": config["model_name"],
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("RAG system initialized successfully")
        return rag_system
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {str(e)}")
        raise

@app.route('/')
def index():
    """Main chat interface."""
    return render_template('chat.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    try:
        if rag_system is None:
            initialize_rag_system()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'vectors': rag_system.faiss_index.ntotal if rag_system else 0,
            'model': system_info.get('model', 'unknown')
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/info')
def api_info():
    """API information endpoint."""
    try:
        if rag_system is None:
            initialize_rag_system()
        
        return jsonify(system_info)
    except Exception as e:
        logger.error(f"Failed to get API info: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@contextmanager
def temporary_api_key(user_api_key: Optional[str]):
    """Context manager for safely handling user API keys without race conditions."""
    if not user_api_key:
        yield
        return
    
    # Store original key
    original_key = os.environ.get('GROQ_API_KEY')
    
    try:
        # Set user's key temporarily
        os.environ['GROQ_API_KEY'] = user_api_key
        logger.info("Using user-provided API key for request")
        yield
    finally:
        # Always restore original key
        if original_key:
            os.environ['GROQ_API_KEY'] = original_key
        else:
            # If there was no original key, remove the user key
            os.environ.pop('GROQ_API_KEY', None)
        logger.debug("API key restored")

def sanitize_input(text: str, max_length: int = 5000) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text or not isinstance(text, str):
        return ""
    
    # Limit length
    text = text[:max_length]
    
    # Remove potentially dangerous characters
    text = html.escape(text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    return text

def validate_session_id(session_id: str) -> str:
    """Validate and sanitize session ID."""
    if not session_id or not isinstance(session_id, str):
        return f'session_{int(time.time())}'
    
    # Only allow alphanumeric characters, underscores, and hyphens
    session_id = re.sub(r'[^a-zA-Z0-9_-]', '', session_id)
    
    # Limit length
    session_id = session_id[:100]
    
    # If empty after sanitization, generate new one
    if not session_id:
        return f'session_{int(time.time())}'
    
    return session_id

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with enhanced response format."""
    # Initialize RAG system if not already done
    if rag_system is None:
        initialize_rag_system()
    
    # Get user API key from headers
    user_api_key = request.headers.get('X-User-API-Key')
    
    # Use context manager to safely handle API key
    with temporary_api_key(user_api_key):
        try:
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({
                    'error': 'Invalid request',
                    'response': 'No data provided.'
                }), 400
            
            # Sanitize and validate inputs
            raw_message = data.get('message', '')
            message = sanitize_input(raw_message).strip()
            session_id = validate_session_id(data.get('sessionId', ''))
            settings = data.get('settings', {}) if isinstance(data.get('settings'), dict) else {}
            
            if not message:
                return jsonify({
                    'error': 'Empty message',
                    'response': 'Please enter a health question.'
                }), 400
            
            # Additional validation
            if len(message) < 3:
                return jsonify({
                    'error': 'Message too short',
                    'response': 'Please enter a more detailed health question.'
                }), 400
            
            # Generate response
            result = rag_system.get_conversation_context(message)
        
            # Format response with enhanced metadata
            response_data = {
                'response': result['response'],
                'timestamp': result['metadata']['timestamp'],
                'sources': result['metadata']['relevant_docs_count'],
                'topScore': result['metadata']['top_doc_score'],
                'sessionId': session_id,
                'metadata': {
                    'model_used': result['metadata']['model_used'],
                    'response_length': result['metadata']['response_length'],
                    'processing_time': result['metadata'].get('processing_time', 0),
                    'sources_used': result['metadata']['relevant_docs_count']
                },
                'sources': []
            }
            
            # Add source information
            for i, doc in enumerate(result['relevant_docs']):
                source_info = {
                    'id': f'source_{i}',
                    'title': f'Source {i + 1}',
                    'content': f'Relevant information from source {i + 1}',
                    'relevanceScore': doc['score'],
                    'metadata': doc['metadata']
                }
                response_data['sources'].append(source_info)
            
            return jsonify(response_data)
            
        except Exception as e:
            logger.error(f"Error in chat endpoint: {str(e)}")
            return jsonify({
                'error': str(e),
                'response': 'I apologize, but I\'m experiencing technical difficulties. Please try again or consult a healthcare professional for immediate medical concerns.',
                'timestamp': datetime.now().isoformat()
            }), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Handle streaming chat messages."""
    try:
        # Initialize RAG system if not already done
        if rag_system is None:
            initialize_rag_system()
        
        # Get request data
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('sessionId', f'session_{int(time.time())}')
        settings = data.get('settings', {})
        
        if not message:
            return jsonify({'error': 'Empty message'}), 400
        
        def generate_stream():
            try:
                # Send initial response
                yield f"data: {json.dumps({'type': 'start', 'data': {'message': 'Starting response generation...'}})}\n\n"
                
                # Generate response
                result = rag_system.get_conversation_context(message)
                
                # Send content in chunks to simulate streaming
                content = result['response']
                chunk_size = 50
                
                for i in range(0, len(content), chunk_size):
                    chunk = content[i:i + chunk_size]
                    yield f"data: {json.dumps({'type': 'content', 'data': {'chunk': chunk}})}\n\n"
                    time.sleep(0.05)  # Small delay for streaming effect
                
                # Send sources
                sources = []
                for i, doc in enumerate(result['relevant_docs']):
                    source_info = {
                        'id': f'source_{i}',
                        'title': f'Source {i + 1}',
                        'content': f'Relevant information from source {i + 1}',
                        'relevanceScore': doc['score'],
                        'metadata': doc['metadata']
                    }
                    sources.append(source_info)
                
                yield f"data: {json.dumps({'type': 'sources', 'data': {'sources': sources}})}\n\n"
                
                # Send completion
                yield f"data: {json.dumps({'type': 'done', 'data': {'timestamp': datetime.now().isoformat()}})}\n\n"
                
            except Exception as e:
                logger.error(f"Error in streaming: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'data': {'error': str(e)}})}\n\n"
        
        return Response(
            stream_with_context(generate_stream()),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
            }
        )
        
    except Exception as e:
        logger.error(f"Error in streaming endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def feedback():
    """Handle user feedback."""
    try:
        data = request.get_json()
        message_id = data.get('messageId')
        rating = data.get('rating')
        feedback_text = data.get('feedback', '')
        
        # Log feedback (in a real app, you'd save to database)
        logger.info(f"Feedback received - Message: {message_id}, Rating: {rating}, Text: {feedback_text}")
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback received successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in feedback endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to process feedback'
        }), 500

@app.route('/api/validate-key', methods=['POST'])
def validate_api_key():
    """Validate a user's Groq API key."""
    try:
        data = request.get_json()
        api_key = data.get('apiKey', '').strip()
        
        if not api_key:
            return jsonify({
                'valid': False,
                'error': 'API key is required'
            }), 400
        
        # Test the API key by making a simple request to Groq
        import requests
        
        test_response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'llama-3.1-8b-instant',
                'messages': [{'role': 'user', 'content': 'test'}],
                'max_tokens': 1
            },
            timeout=10
        )
        
        if test_response.status_code == 200:
            return jsonify({
                'valid': True,
                'message': 'API key is valid'
            })
        else:
            return jsonify({
                'valid': False,
                'error': 'Invalid API key'
            }), 400
            
    except requests.exceptions.Timeout:
        return jsonify({
            'valid': False,
            'error': 'API key validation timed out'
        }), 408
    except Exception as e:
        logger.error(f"Error validating API key: {str(e)}")
        return jsonify({
            'valid': False,
            'error': 'Failed to validate API key'
        }), 500

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get chat sessions (placeholder for future implementation)."""
    return jsonify({'sessions': []})

@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a chat session (placeholder for future implementation)."""
    return jsonify({'status': 'success', 'message': 'Session deleted'})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

def create_templates():
    """Create HTML templates if they don't exist."""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    chat_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Health Chatbot - AI Medical Assistant</title>
    <meta name="description" content="AI-powered health chatbot with RAG technology for medical questions and health guidance" />
    
    <!-- Preload fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        #root {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            color: white;
            text-align: center;
        }
        
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255,255,255,0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div id="root">
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <h1>🏥 Health Chatbot</h1>
            <p>Loading AI Medical Assistant...</p>
            <p style="margin-top: 20px; opacity: 0.8;">
                If this takes too long, please check your internet connection.
            </p>
        </div>
    </div>
    
    <script>
        // Redirect to frontend if available
        setTimeout(() => {
            window.location.href = 'http://localhost:3000';
        }, 2000);
    </script>
</body>
</html>'''
    
    with open(os.path.join(templates_dir, 'chat.html'), 'w', encoding='utf-8') as f:
        f.write(chat_html)

def main():
    """Main function to run the enhanced web chatbot."""
    print("🌐 Starting Enhanced Health Chatbot Web Interface...")
    
    # Check for Groq API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Error: GROQ_API_KEY environment variable not set.")
        print("Please set your Groq API key and try again.")
        return
    
    # Create templates
    create_templates()
    
    # Initialize RAG system
    try:
        initialize_rag_system()
        print("✅ RAG system initialized successfully!")
        print(f"📊 Vector database: {rag_system.faiss_index.ntotal:,} documents")
        print(f"🤖 LLM Model: {system_info['model']}")
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {str(e)}")
        return
    
    # Run Flask app
    print("🚀 Starting enhanced web server...")
    print("📱 Backend API: http://localhost:5000")
    print("📱 Frontend: http://localhost:3000 (if running)")
    print("🛑 Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()

