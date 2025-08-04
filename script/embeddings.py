from sentence_transformers import SentenceTransformer
import torch
import os

def load_embedding_model():
    """Load your pre-downloaded mpnet model"""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    
    model_path = os.path.join(current_dir, "..", "models", "all-mpnet-base-v2")
    model_path = os.path.abspath(model_path)
    
    print(f"Looking for model at: {model_path}")
    
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model directory not found: {model_path}")
    
    
    required_files = ['config.json', 'pytorch_model.bin']
    for file in required_files:
        file_path = os.path.join(model_path, file)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Model file missing: {file_path}")
    
    return SentenceTransformer(
        model_path,
        device='cuda' if torch.cuda.is_available() else 'cpu'
    )

def generate_embeddings(text, model):
    """Generate embeddings with mpnet"""
    return model.encode(text)