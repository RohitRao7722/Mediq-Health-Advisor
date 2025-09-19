# 🏥 Health Chatbot RAG System

A comprehensive Retrieval-Augmented Generation (RAG) system for health-related queries, powered by Groq's Llama 3.1 8B model and a custom vector database of medical information.

## 🚀 Features

- **Vector Search**: Fast similarity search across 303,409 health documents
- **Groq Integration**: Powered by Llama 3.1 8B Instant model
- **Multiple Interfaces**: Command-line, web interface, and API
- **Health-Focused**: Specialized for medical queries with safety features
- **Source Attribution**: Tracks and displays information sources
- **Medical Disclaimers**: Built-in safety warnings and disclaimers

## 📊 System Architecture

```
User Query → Vector Search → Document Retrieval → LLM Prompt → Response
     ↓              ↓              ↓              ↓           ↓
Health Query → FAISS Index → Relevant Docs → Groq LLM → Natural Response
```

## 🛠️ Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up for a free account
3. Generate an API key
4. Set environment variable:

```bash
export GROQ_API_KEY='your-api-key-here'
```

### 3. Verify Vector Database

Ensure these files exist:
- `vector_index.idx` (FAISS index)
- `vector_metadata.pkl` (Document metadata)

If missing, run:
```bash
python src/batch_embedding_processor.py
```

## 🚀 Quick Start

### Option 1: Automated Setup

```bash
python setup_rag_system.py
```

### Option 2: Manual Setup

1. **Test the system:**
```bash
python src/test_rag_system.py
```

2. **Run command-line chatbot:**
```bash
python src/rag_system.py
```

3. **Start web interface:**
```bash
python src/web_chatbot.py
```

## 📱 Usage

### Command-Line Interface

```bash
python src/rag_system.py
```

Example conversation:
```
You: What are the symptoms of diabetes?
AI: Based on the medical information available, common symptoms of diabetes include:
- Increased thirst and frequent urination
- Extreme fatigue and weakness
- Blurred vision
- Slow-healing sores or frequent infections
- Unexplained weight loss (Type 1)
- Tingling or numbness in hands/feet

[Medical disclaimer and source information...]
```

### Web Interface

```bash
python src/web_chatbot.py
```

Then open: http://localhost:5000

### API Usage

```python
from src.rag_system import HealthRAGSystem

# Initialize system
rag = HealthRAGSystem()
rag.load_search_system()

# Get response
response = rag.chat("What are the symptoms of diabetes?")
print(response)
```

## 🔧 Configuration

### RAG System Parameters

```python
config = {
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",  # Embedding model
    "index_path": "vector_index.idx",                        # FAISS index path
    "metadata_path": "vector_metadata.pkl",                  # Metadata path
    "groq_model": "llama-3.1-8b-instant"                    # Groq model
}
```

### Search Parameters

- **Top-k documents**: 5 (configurable)
- **Temperature**: 0.3 (for consistent medical responses)
- **Max tokens**: 1000
- **Search timeout**: 30 seconds

## 📚 Data Sources

The system searches across:

1. **Medical Q&A Database** (ai-medical-chatbot.csv)
   - Real patient-doctor conversations
   - Symptom descriptions and treatments

2. **Medical Knowledge Base** (medquad.csv)
   - Structured medical information
   - Treatment protocols and guidelines

3. **NIH Health Topics** (NIH MedlinePlus)
   - Authoritative health information
   - Evidence-based medical content

4. **WHO Health Guidelines** (WHO documents)
   - Official health recommendations
   - Global health standards

## 🛡️ Safety Features

### Medical Disclaimers

Every response includes:
- Clear medical disclaimer
- Emphasis on professional consultation
- Emergency care instructions
- Source attribution

### Response Quality

- **Temperature 0.3**: Consistent, factual responses
- **Source tracking**: All information is traceable
- **Relevance scoring**: Only most relevant documents used
- **Error handling**: Graceful failure with fallback messages

## 📊 Performance

### Search Performance
- **Search speed**: ~0.03 seconds per query
- **Queries per second**: ~25-30
- **Vector database**: 303,409 documents
- **Memory usage**: ~2-3 GB RAM

### Response Quality
- **Relevance**: High-quality medical information
- **Accuracy**: Based on authoritative sources
- **Completeness**: Comprehensive health coverage
- **Safety**: Built-in medical disclaimers

## 🔍 Testing

### Automated Tests

```bash
python src/test_rag_system.py
```

Tests include:
- System initialization
- Search functionality
- Response generation
- Error handling
- Performance benchmarks

### Manual Testing

```bash
python src/test_search_interface.py
```

Comprehensive health query testing with 28+ test cases.

## 🚨 Troubleshooting

### Common Issues

1. **Groq API Key Error**
   ```
   Error: GROQ_API_KEY environment variable not set
   ```
   Solution: Set your Groq API key as an environment variable

2. **Vector Database Missing**
   ```
   Error: vector_index.idx not found
   ```
   Solution: Run the embedding generation process first

3. **Memory Issues**
   ```
   Error: Out of memory
   ```
   Solution: Ensure you have at least 4GB RAM available

4. **Slow Performance**
   - Check CPU usage
   - Ensure no other heavy processes running
   - Consider reducing batch size

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Monitoring

### Health Check Endpoint

```bash
curl http://localhost:5000/health
```

### API Information

```bash
curl http://localhost:5000/api/info
```

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Voice interface
- [ ] Mobile app
- [ ] User authentication
- [ ] Conversation history
- [ ] Advanced medical reasoning
- [ ] Integration with medical databases
- [ ] Real-time health monitoring

## 📄 License

This project is for educational and research purposes. Please ensure compliance with medical data usage regulations in your jurisdiction.

## ⚠️ Important Notes

- **Not a substitute for medical advice**: Always consult healthcare professionals
- **Emergency situations**: Call emergency services immediately
- **Data privacy**: Ensure compliance with healthcare data regulations
- **Model limitations**: AI responses may not always be accurate
- **Regular updates**: Keep the system updated with latest medical information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Ensure all dependencies are installed
4. Verify API keys and file paths

---

**Remember**: This is an AI assistant for general health information only. Always consult qualified healthcare professionals for medical advice, diagnosis, or treatment.

