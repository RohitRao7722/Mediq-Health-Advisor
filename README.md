# 🏥 Personalized Health Chatbot

An AI-powered health chatbot with Retrieval-Augmented Generation (RAG) for accurate and sourced health information.

## 🚀 Features

- **Medical Knowledge Base**: 303,409 health documents from NIH MedlinePlus and WHO
- **Accurate Information**: RAG system that grounds responses in reliable medical sources
- **Source Citations**: All responses include links to source documents
- **Modern UI**: Responsive design that works on desktop and mobile
- **API Key Management**: Use your own Groq API key or a shared key
- **Streaming Responses**: Real-time generation of responses

## 🛠️ Technology Stack

### Backend
- **Framework**: Python/Flask
- **AI Model**: Llama-3.1-8b-instant via Groq API
- **Vector Database**: FAISS with 466MB health knowledge index
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2

### Frontend
- **Framework**: React + TypeScript + Vite
- **UI Library**: Material-UI (MUI)
- **State Management**: Zustand
- **API Client**: Axios

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+
- Groq API key

## 🏁 Getting Started

### Clone the Repository

```bash
git clone https://github.com/yourusername/personalized-health-chatbot.git
cd personalized-health-chatbot
```

### Backend Setup

1. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # OR
   source .venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Running the Application

Use the provided startup script to launch both backend and frontend:

```bash
python start_frontend.py
```

Alternatively, you can start them separately:

**Backend**:
```bash
python src/enhanced_web_chatbot.py
```

**Frontend**:
```bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 📊 Project Structure

```
├── src/                      # Backend source files
│   ├── enhanced_web_chatbot.py  # Main Flask server
│   ├── rag_system.py         # RAG implementation
│   └── chunking.py           # Document processing
├── frontend/                 # React frontend
│   ├── src/                  # Frontend source code
│   └── public/               # Static assets
├── vector_index.idx          # FAISS vector index
├── vector_metadata.pkl       # Document metadata
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables
```

## 🚢 Deployment

For production deployment:

1. Build the frontend:
   ```bash
   cd frontend
   npm run build
   ```

2. Deploy the backend with production settings:
   ```bash
   export FLASK_ENV=production
   python src/enhanced_web_chatbot.py
   ```

3. Serve the frontend build directory with a web server like Nginx.

## 📜 License

This project is licensed under the MIT License.
