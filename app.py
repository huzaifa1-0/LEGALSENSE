# Fix for Streamlit event loop error
import sys
import asyncio

if sys.platform == "win32":
    if sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import os
os.environ["STREAMLIT_SERVER_ENABLE_FILE_WATCHER"] = "false"

import streamlit as st
import pandas as pd
import numpy as np
from script.embeddings import load_embedding_model, generate_embeddings
from script.retrieval import find_relevant_chunks
from script.promp_engineering import create_legal_prompt
from script.generation import load_falcon_model, generate_answer

# Initialize models
@st.cache_resource
def load_models():
    try:
        embed_model = load_embedding_model()
        st.success("Embedding model loaded successfully")
    except Exception as e:
        st.error(f"Error loading embedding model: {str(e)}")
        embed_model = None
    
    try:
        falcon_tokenizer, falcon_model = load_falcon_model()
        st.success("Falcon model loaded successfully")
    except Exception as e:
        st.error(f"Error loading Falcon model: {str(e)}")
        falcon_tokenizer, falcon_model = None, None
    
    return embed_model, falcon_tokenizer, falcon_model

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("U:\\LEGALSENSE\\chunks_and_embeddings.csv")
        st.success("Knowledge base loaded successfully")
        return df
    except Exception as e:
        st.error(f"Error loading knowledge base: {str(e)}")
        return pd.DataFrame()

def main():
    st.set_page_config(page_title="Pakistan Legal Assistant", layout="wide")
    st.title("🇵🇰 Pakistan Penal Code Expert")
    st.caption("AI Legal Assistant powered by Falcon-RW-1B and mpnet embeddings")
    
    # Initialize session state
    if "history" not in st.session_state:
        st.session_state.history = []
    
    # Load resources
    with st.spinner("Loading AI models..."):
        embed_model, falcon_tokenizer, falcon_model = load_models()
    
    with st.spinner("Loading legal database..."):
        df = load_data()
    
    # User input
    query = st.chat_input("Ask your legal question about Pakistan Penal Code...")
    
    if query:
        # Add to history
        st.session_state.history.append(("user", query))
        
        try:
            # Show processing status
            with st.status("Analyzing legal provisions...", expanded=False):
                # 1. Generate query embedding
                query_embedding = generate_embeddings(query, embed_model)
                
                # 2. Retrieve relevant context
                relevant_chunks = find_relevant_chunks(query_embedding, df)
                context = "\n\n".join([
                    f"Page {row['page_number']}: {row['sentence_chunk']}" 
                    for _, row in relevant_chunks.iterrows()
                ])
                
                # 3. Create legal-optimized prompt
                prompt = create_legal_prompt(context, query)
                
                # 4. Generate answer
                answer = generate_answer(prompt, falcon_tokenizer, falcon_model)
                
                # 5. Format sources
                sources = []
                for _, row in relevant_chunks.iterrows():
                    sources.append({
                        "page": row["page_number"],
                        "content": row["sentence_chunk"]
                    })
            
            # Add to history
            st.session_state.history.append(("assistant", answer, sources))
            
        except Exception as e:
            st.error(f"Error processing your request: {str(e)}")
            st.session_state.history.append(("assistant", "Sorry, I encountered an error processing your request"))
    
    # Display conversation
    for i, entry in enumerate(st.session_state.history):
        role = entry[0]
        
        with st.chat_message(role.capitalize()):
            # Display message
            st.write(entry[1])
            
            # Display sources for assistant
            if role == "assistant" and len(entry) > 2:
                _, answer, sources = entry
                
                # Sources expander
                with st.expander(f"📚 Legal Sources ({len(sources)} provisions)"):
                    for source in sources:
                        st.caption(f"**Page {source['page']}**")
                        st.write(source["content"])
                        st.divider()

if __name__ == "__main__":
    main()