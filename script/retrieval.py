import numpy as np
import pandas as pd
import re

def parse_embedding_string(embed_str):
    """Safely parse embedding string from CSV"""
    
    if not isinstance(embed_str, str):
        return embed_str
        
    
    cleaned = re.sub(r'[\[\]\s]+', ' ', embed_str).strip()
    
    
    if ',' in cleaned:
        parts = cleaned.split(',')
    else:
        parts = cleaned.split()
    
    
    return np.array([float(part) for part in parts if part], dtype=np.float32)

def find_relevant_chunks(query_embedding, df, top_k=3):
    """Find top relevant legal provisions"""
    
    embeddings_list = [parse_embedding_string(x) for x in df['embedding']]
    chunk_embeds = np.stack(embeddings_list)
    
    
    norms = np.linalg.norm(chunk_embeds, axis=1)
    norm_query = np.linalg.norm(query_embedding)
    similarities = np.dot(chunk_embeds, query_embedding) / (norms * norm_query + 1e-8)
    
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return df.iloc[top_indices]