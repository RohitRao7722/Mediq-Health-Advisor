"""
Web-based Health Chatbot Interface

A simple Flask web interface for the Health RAG System.
"""

import os
import sys
import logging
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import uuid

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_system import HealthRAGSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global RAG system instance
rag_system = None


def initialize_rag_system():
    """Initialize the RAG system."""
    global rag_system
    
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
        
        logger.info("RAG system initialized successfully")
        return rag_system
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {str(e)}")
        raise


@app.route('/')
def index():
    """Main chat interface."""
    return render_template('chat.html')


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        # Initialize RAG system if not already done
        if rag_system is None:
            initialize_rag_system()
        
        # Get user message
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'error': 'Empty message',
                'response': 'Please enter a health question.'
            })
        
        # Generate response
        result = rag_system.get_conversation_context(message)
        
        # Format response
        response_data = {
            'response': result['response'],
            'timestamp': result['metadata']['timestamp'],
            'sources': len(result['relevant_docs']),
            'top_score': result['metadata']['top_doc_score']
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'response': 'I apologize, but I\'m experiencing technical difficulties. Please try again or consult a healthcare professional for immediate medical concerns.'
        })


@app.route('/health')
def health_check():
    """Health check endpoint."""
    try:
        if rag_system is None:
            initialize_rag_system()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'vectors': rag_system.faiss_index.ntotal if rag_system else 0
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })


@app.route('/api/info')
def api_info():
    """API information endpoint."""
    try:
        if rag_system is None:
            initialize_rag_system()
        
        return jsonify({
            'model': rag_system.groq_model,
            'vectors': rag_system.faiss_index.ntotal,
            'embedding_model': rag_system.model_name,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })


def create_templates():
    """Create HTML templates if they don't exist."""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    chat_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Health Chatbot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 80vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .chat-header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message.bot {
            justify-content: flex-start;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        
        .message.user .message-content {
            background: #007bff;
            color: white;
        }
        
        .message.bot .message-content {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
        }
        
        .chat-input {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
        }
        
        .input-group input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .input-group input:focus {
            border-color: #007bff;
        }
        
        .input-group button {
            padding: 12px 24px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        
        .input-group button:hover {
            background: #0056b3;
        }
        
        .input-group button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .loading {
            display: none;
            text-align: center;
            color: #666;
            font-style: italic;
        }
        
        .disclaimer {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #856404;
        }
        
        .disclaimer strong {
            color: #d63031;
        }
        
        .typing-indicator {
            display: none;
            align-items: center;
            gap: 5px;
            color: #666;
            font-style: italic;
        }
        
        .typing-dots {
            display: flex;
            gap: 2px;
        }
        
        .typing-dots span {
            width: 4px;
            height: 4px;
            background: #666;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }
        
        .typing-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dots span:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
            }
            30% {
                transform: translateY(-10px);
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🏥 Health Chatbot</h1>
            <p>Ask me about health, symptoms, treatments, and wellness</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="disclaimer">
                <strong>Medical Disclaimer:</strong> This AI assistant provides general health information only. 
                It is NOT a substitute for professional medical advice, diagnosis, or treatment. 
                Always consult with qualified healthcare professionals for medical concerns. 
                In case of medical emergency, call emergency services immediately.
            </div>
            
            <div class="message bot">
                <div class="message-content">
                    Hello! I'm your AI health assistant. I can help answer questions about:
                    <br>• Symptoms and conditions
                    <br>• Treatments and medications
                    <br>• Preventive care
                    <br>• General health advice
                    <br><br>What would you like to know about your health?
                </div>
            </div>
        </div>
        
        <div class="chat-input">
            <div class="input-group">
                <input type="text" id="messageInput" placeholder="Ask a health question..." autocomplete="off">
                <button id="sendButton" onclick="sendMessage()">Send</button>
            </div>
            <div class="loading" id="loading">AI is thinking...</div>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const loading = document.getElementById('loading');
        
        // Allow sending message with Enter key
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Auto-focus input
        messageInput.focus();
        
        function addMessage(content, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            
            messageDiv.appendChild(contentDiv);
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function showLoading() {
            loading.style.display = 'block';
            sendButton.disabled = true;
            messageInput.disabled = true;
        }
        
        function hideLoading() {
            loading.style.display = 'none';
            sendButton.disabled = false;
            messageInput.disabled = false;
        }
        
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;
            
            // Add user message
            addMessage(message, true);
            messageInput.value = '';
            
            // Show loading
            showLoading();
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    addMessage(`Error: ${data.error}`);
                } else {
                    addMessage(data.response);
                }
                
            } catch (error) {
                addMessage('Sorry, I encountered an error. Please try again.');
                console.error('Error:', error);
            } finally {
                hideLoading();
                messageInput.focus();
            }
        }
    </script>
</body>
</html>'''
    
    with open(os.path.join(templates_dir, 'chat.html'), 'w', encoding='utf-8') as f:
        f.write(chat_html)


def main():
    """Main function to run the web chatbot."""
    print("🌐 Starting Health Chatbot Web Interface...")
    
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
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {str(e)}")
        return
    
    # Run Flask app
    print("🚀 Starting web server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == "__main__":
    main()

