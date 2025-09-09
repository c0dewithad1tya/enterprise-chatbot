"""
Create Vector Index for Documents
==================================
This script creates FAISS vector embeddings for all markdown documents
"""

import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from typing import List, Dict

def load_document_chunks(chunks_file: str = 'document_chunks_improved.json') -> List[Dict]:
    """Load document chunks from JSON file"""
    with open(chunks_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_vector_index(chunks: List[Dict], model_name: str = 'all-MiniLM-L6-v2'):
    """Create FAISS index from document chunks"""
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    
    # Extract texts for embedding
    texts = [chunk['content'] for chunk in chunks]
    
    print(f"Creating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Create FAISS index
    dimension = embeddings.shape[1]  # 384 for all-MiniLM-L6-v2
    index = faiss.IndexFlatL2(dimension)
    
    # Add embeddings to index
    index.add(embeddings.astype('float32'))
    
    print(f"Created FAISS index with {index.ntotal} vectors")
    
    return index, embeddings

def save_index(index, chunks, embeddings, index_path: str = 'faiss_index'):
    """Save FAISS index and metadata"""
    # Save FAISS index
    faiss.write_index(index, f"{index_path}.index")
    print(f"Saved FAISS index to {index_path}.index")
    
    # Save chunks and metadata
    metadata = {
        'chunks': chunks,
        'embeddings_shape': embeddings.shape
    }
    
    with open(f"{index_path}_metadata.pkl", 'wb') as f:
        pickle.dump(metadata, f)
    print(f"Saved metadata to {index_path}_metadata.pkl")
    
    # Also save embeddings for debugging
    np.save(f"{index_path}_embeddings.npy", embeddings)
    print(f"Saved embeddings to {index_path}_embeddings.npy")

def test_search(index, chunks, model, query: str = "What technologies are used?", k: int = 5):
    """Test the search functionality"""
    print(f"\nTesting search with query: '{query}'")
    
    # Encode query
    query_embedding = model.encode([query])
    
    # Search
    distances, indices = index.search(query_embedding.astype('float32'), k)
    
    print(f"\nTop {k} results:")
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        chunk = chunks[idx]
        print(f"\n{i+1}. Document: {chunk['document_title']}")
        print(f"   Distance: {dist:.4f}")
        print(f"   Preview: {chunk['content'][:100]}...")

def main():
    """Main function to create vector index"""
    # Load chunks
    print("Loading document chunks...")
    chunks = load_document_chunks()
    print(f"Loaded {len(chunks)} chunks")
    
    # Create vector index
    index, embeddings = create_vector_index(chunks)
    
    # Save index
    save_index(index, chunks, embeddings)
    
    # Test with some queries
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    test_queries = [
        "What technologies are used in the frontend?",
        "What is the technology stack?",
        "Tell me about the deployment process",
        "Who are the team members?",
        "What is the system architecture?"
    ]
    
    for query in test_queries:
        test_search(index, chunks, model, query, k=3)
    
    print("\n✅ Vector index created successfully!")
    print("Files created:")
    print("  - faiss_index.index (FAISS index)")
    print("  - faiss_index_metadata.pkl (chunks and metadata)")
    print("  - faiss_index_embeddings.npy (raw embeddings)")

if __name__ == "__main__":
    main()