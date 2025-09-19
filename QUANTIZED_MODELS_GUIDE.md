# Quantized Embedding Models for CPU-Only Systems

## 🚀 Best Quantized Models for i5 CPU Systems

Based on my research, here are the most suitable quantized embedding models for your health chatbot:

### 1. **sentence-transformers/all-MiniLM-L6-v2** (Recommended)
- **Model Size**: ~22MB
- **Embedding Dimension**: 384
- **Quantization**: Native CPU optimization
- **Performance**: Excellent balance of speed and accuracy
- **CPU Usage**: Optimized for i5 processors

### 2. **sentence-transformers/all-MiniLM-L12-v2** (Higher Quality)
- **Model Size**: ~33MB
- **Embedding Dimension**: 384
- **Performance**: Better accuracy than L6-v2
- **CPU Usage**: Slightly slower but still CPU-optimized

### 3. **sentence-transformers/paraphrase-MiniLM-L6-v2** (Multilingual)
- **Model Size**: ~22MB
- **Embedding Dimension**: 384
- **Performance**: Good for multilingual content
- **CPU Usage**: Optimized for CPU inference

## 📊 Performance Estimates for Your System

Based on your **8.3M chunks**:

| Model | Estimated Time | Memory Usage | Accuracy |
|-------|---------------|--------------|----------|
| all-MiniLM-L6-v2 | **2.5-3 hours** | ~2GB RAM | High |
| all-MiniLM-L12-v2 | **3.5-4 hours** | ~2.5GB RAM | Very High |
| paraphrase-MiniLM-L6-v2 | **2.5-3 hours** | ~2GB RAM | High |

## 🔧 Installation and Usage

### Install Required Libraries
```bash
pip install sentence-transformers faiss-cpu torch numpy tqdm
```

### Basic Usage Code
```python
from sentence_transformers import SentenceTransformer
import torch
import os

# Force CPU usage
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Load optimized model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu')

# Optimize for CPU
torch.set_num_threads(4)  # Adjust based on your i5 cores

# Generate embeddings
sentences = ["Your text here"]
embeddings = model.encode(sentences, convert_to_numpy=True)
```

## 🚀 Advanced Quantized Models (If Available)

### 1. **nixiesearch/e5-base-v2-onnx** (ONNX Optimized)
- **Format**: ONNX with QInt8 quantization
- **Performance**: Very fast CPU inference
- **Usage**: Requires ONNX Runtime

```python
# Install ONNX Runtime
pip install onnxruntime

# Load ONNX model
from transformers import AutoTokenizer, AutoModel
import onnxruntime as ort

tokenizer = AutoTokenizer.from_pretrained('nixiesearch/e5-base-v2-onnx')
model = AutoModel.from_pretrained('nixiesearch/e5-base-v2-onnx')
```

### 2. **second-state/All-MiniLM-L6-v2-Embedding-GGUF** (GGUF Format)
- **Format**: GGUF with various quantization levels
- **Performance**: Extremely fast CPU inference
- **Usage**: Requires llama.cpp or similar

## 💡 Optimization Tips for Your i5 System

### 1. **Memory Optimization**
```python
# Process in smaller batches
batch_size = 128  # Adjust based on available RAM

# Use memory-efficient processing
torch.set_num_threads(4)  # Match your CPU cores
```

### 2. **CPU Optimization**
```python
# Set optimal number of threads
import torch
torch.set_num_threads(4)  # For i5-4core

# Disable GPU completely
os.environ["CUDA_VISIBLE_DEVICES"] = ""
```

### 3. **Batch Processing**
```python
# Process large datasets in chunks
def process_large_dataset(texts, batch_size=128):
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = model.encode(batch, convert_to_numpy=True)
        all_embeddings.append(embeddings)
    return np.vstack(all_embeddings)
```

## 🎯 Recommended Implementation

For your health chatbot with 8.3M chunks, I recommend:

1. **Start with**: `sentence-transformers/all-MiniLM-L6-v2`
2. **Batch size**: 128 (optimized for i5)
3. **Expected time**: 2.5-3 hours
4. **Memory usage**: ~2GB RAM

## 🔄 Alternative: Progressive Processing

If you want to start testing immediately:

```python
# Process a subset first (e.g., 100K chunks)
subset_docs = chunked_docs[:100000]  # First 100K chunks
embeddings = model.encode([doc.page_content for doc in subset_docs])
```

This will take only ~2-3 minutes and let you test the system before processing all 8.3M chunks.

## 📈 Monitoring Progress

The optimized script includes:
- Real-time progress bars
- Time estimates
- Memory usage monitoring
- Processing speed metrics

Run with: `python src/optimized_embedding_and_vectorstore.py`


