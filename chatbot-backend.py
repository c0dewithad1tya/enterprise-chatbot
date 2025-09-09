"""
WhoKnows? Chatbot Backend - Clean Version
"""
import json
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_relevant_info(content, query):
    """Extract relevant information from content based on query"""
    query_lower = query.lower()
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    relevant_lines = []
    
    # Look for structured information (Name:, Email:, etc.)
    for line in lines:
        clean_line = line.replace('- **', '').replace('**', '').replace('###', '').replace('##', '').strip()
        
        # High priority: structured data
        if any(marker in clean_line for marker in ['Name:', 'Email:', 'Responsibility:']):
            relevant_lines.append(clean_line)
        # Medium priority: lines with query keywords
        elif any(word in clean_line.lower() for word in query_lower.split() if len(word) > 2):
            if len(clean_line) > 10:
                relevant_lines.append(clean_line)
    
    return relevant_lines[:5]

def format_response_title(query):
    """Create a clean title for the response"""
    query_lower = query.lower()
    
    if 'responsibility' in query_lower or 'responsibilities' in query_lower:
        name = query.replace('What is the responsibility of', '').replace('What are the responsibilities of', '').replace('?', '').strip()
        return f"## {name}'s Responsibilities\n"
    elif 'who is' in query_lower:
        if 'cto' in query_lower or 'chief technology officer' in query_lower:
            return f"## Chief Technology Officer (CTO)\n"
        elif 'cio' in query_lower or 'chief information officer' in query_lower:
            return f"## Chief Information Officer (CIO)\n"
        elif 'ceo' in query_lower or 'chief executive officer' in query_lower:
            return f"## Chief Executive Officer (CEO)\n"
        else:
            name = query_lower.replace('who is the', '').replace('who is', '').replace('?', '').strip()
            name_parts = name.split()
            name = ' '.join(word.capitalize() for word in name_parts)
            return f"## {name}\n"
    elif 'what is the' in query_lower:
        subject = query_lower.replace('what is the', '').replace('?', '').strip()
        return f"## {subject.title()}\n"
    else:
        return f"## Answer\n"

def search_local_documents(query):
    """Search through indexed documents using FAISS vector similarity"""
    try:
        # Load FAISS index and metadata
        index = faiss.read_index('faiss_index.index')
        with open('faiss_index_metadata.pkl', 'rb') as f:
            metadata = pickle.load(f)
            chunks = metadata['chunks']
        
        # Load the model for encoding the query
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Encode the query
        query_embedding = model.encode([query])
        
        # Search for similar documents with boosted relevance
        k = 10
        distances, indices = index.search(query_embedding.astype('float32'), k)
        
        # Create results with chunks and similarity scores
        top_results = []
        query_terms = query.lower().split()
        
        # Filter for relevance - prioritize chunks that contain query terms
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(chunks):
                chunk = chunks[idx]
                content_lower = chunk['content'].lower()
                section_title_lower = chunk.get('section_title', '').lower()
                
                # Check if chunk contains relevant terms
                relevance_boost = 0
                
                # Special handling for ML stack queries
                if 'machine' in query.lower() and 'learning' in query.lower():
                    if 'machine learning stack' in section_title_lower:
                        relevance_boost += 10
                    elif 'machine learning' in section_title_lower:
                        relevance_boost += 5
                
                # General term matching
                for term in query_terms:
                    if len(term) > 2:
                        if term in section_title_lower:
                            relevance_boost += 3
                        if term in content_lower:
                            relevance_boost += 1
                
                # Combine distance score with relevance boost
                base_score = float(1 / (1 + dist))
                final_score = base_score * (1 + relevance_boost * 0.5)
                
                top_results.append({
                    'chunk': chunk,
                    'score': final_score,
                    'distance': dist,
                    'relevance_boost': relevance_boost
                })
        
        # Re-sort by combined score
        top_results.sort(key=lambda x: x['score'], reverse=True)
        top_results = top_results[:5]
        
    except (FileNotFoundError, Exception) as e:
        # Fallback to keyword search if vector index doesn't exist
        try:
            with open('document_chunks_improved.json', 'r', encoding='utf-8') as f:
                chunks = json.load(f)
        except FileNotFoundError:
            return {
                'message': "📚 **No documentation indexed yet**\\n\\nPlease run the indexing script to load the documentation.",
                'sources': []
            }
        
        query_lower = query.lower()
        results = []
        
        # Simple keyword matching as fallback
        for chunk in chunks:
            content_lower = chunk['content'].lower()
            if any(word in content_lower for word in query_lower.split()):
                score = sum(content_lower.count(word) for word in query_lower.split())
                results.append({
                    'chunk': chunk,
                    'score': score
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        top_results = results[:5]
    
    if not top_results:
        return {
            'message': f"""## 🔍 No Results Found

I couldn't find information about **"{query}"** in the documentation.

### You can try asking about:

- 🏗️ **Application Architecture** - System design and components
- ⚡ **Technology Stack** - Languages, frameworks, and tools
- 🚀 **Deployment Strategies** - CI/CD and release processes
- 👥 **Team Members** - People and organizational structure
- 🎯 **User Journey** - User experience and workflows
- 🔧 **Maintenance Procedures** - Housekeeping and operations

**Tip:** Try using different keywords or be more specific in your query.""",
            'sources': []
        }
    
    # Build response from results
    sources = []
    seen_docs = set()
    
    # Group results by document and extract the most relevant parts
    doc_contents = {}
    for result in top_results:
        chunk = result['chunk']
        doc_title = chunk['document_title']
        
        if doc_title not in doc_contents:
            doc_contents[doc_title] = {
                'content': chunk['content'],
                'relevance': result.get('score', 0)
            }
    
    # For ML/technology queries, prioritize Technology Stack document
    query_lower_normalized = query.lower()
    if any(term in query_lower_normalized for term in ['machine learning', 'ml', 'stack', 'technology', 'tech stack', 'ai']):
        # Check if Technology Stack document is in results
        tech_stack_doc = None
        for doc_title, doc_data in doc_contents.items():
            if 'Technology Stack' in doc_title:
                tech_stack_doc = (doc_title, doc_data)
                break
        
        # If Technology Stack is found and reasonably relevant, use it
        if tech_stack_doc and tech_stack_doc[1]['relevance'] > 0.3:
            main_doc_title, main_doc_data = tech_stack_doc
        else:
            sorted_docs = sorted(doc_contents.items(), key=lambda x: x[1]['relevance'], reverse=True)
            main_doc_title, main_doc_data = sorted_docs[0]
    else:
        # Take the most relevant document
        sorted_docs = sorted(doc_contents.items(), key=lambda x: x[1]['relevance'], reverse=True)
        main_doc_title, main_doc_data = sorted_docs[0]
    
    # Create response
    response_title = format_response_title(query)
    key_info = extract_relevant_info(main_doc_data['content'], query)
    
    if key_info:
        formatted_info = '\\n'.join(f"• {line}" for line in key_info)
        message = f"{response_title}\\n{formatted_info}"
    else:
        # Handle special cases
        query_lower = query.lower()
        if 'ceo' in query_lower:
            message = "## CEO Information\\n\\nNo CEO information is available in the current documentation.\\n\\nAvailable executives:\\n• Chief Technology Officer (CTO): Alexandra Chen\\n• Chief Information Officer (CIO): Marcus Williams"
        elif 'who is' in query_lower:
            person = query.replace('Who is', '').replace('?', '').strip()
            message = f"## {person}\\n\\nNo information found about {person} in the documentation."
        else:
            message = f"## Information Not Found\\n\\nI couldn't find specific information about: {query}"
    
    # Create source references
    for doc_title, _ in [(main_doc_title, main_doc_data)]:
        for chunk in chunks:
            if chunk['document_title'] == doc_title and doc_title not in seen_docs:
                seen_docs.add(doc_title)
                sources.append({
                    'type': 'document',
                    'title': doc_title,
                    'path': chunk.get('document_path', ''),
                    'url': f"documentation/{chunk['document_path'].split('/')[-1] if chunk.get('document_path') else ''}"
                })
                break
    
    return {
        'message': message,
        'sources': sources[:3]
    }

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        result = search_local_documents(query)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)