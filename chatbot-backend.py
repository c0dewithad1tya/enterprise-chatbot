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

def expand_query_terms(query):
    """Expand query with synonyms and related terms"""
    query_lower = query.lower()
    expanded_terms = query_lower.split()
    
    # Add synonyms and expansions
    synonyms = {
        'ml': ['machine learning', 'ai', 'artificial intelligence'],
        'tech': ['technology', 'technical'],
        'stack': ['technology stack', 'tech stack', 'technologies'],
        'cto': ['chief technology officer', 'technology officer'],
        'cio': ['chief information officer', 'information officer'],
        'backend': ['back-end', 'server', 'api'],
        'frontend': ['front-end', 'ui', 'interface'],
        'database': ['db', 'storage', 'data store']
    }
    
    for term in query_lower.split():
        if term in synonyms:
            expanded_terms.extend(synonyms[term])
    
    return expanded_terms

def extract_relevant_info(content, query):
    """Extract relevant information from content based on query with improved logic"""
    query_terms = expand_query_terms(query)
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    relevant_lines = []
    
    # Score lines based on relevance
    scored_lines = []
    for line in lines:
        clean_line = line.replace('- **', '').replace('**', '').replace('###', '').replace('##', '').replace('#', '').strip()
        if len(clean_line) < 10:
            continue
            
        score = 0
        clean_lower = clean_line.lower()
        
        # High priority: structured data (Name, Email, Version, etc.)
        if any(marker in clean_line for marker in ['Name:', 'Email:', 'Responsibility:', 'Version:', 'Purpose:', 'Features:', 'Models:', 'Library:']):
            score += 10
        
        # Medium priority: technical specifications
        if any(marker in clean_lower for marker in ['**version**', '**models**', '**features**', '**developer**', '**purpose**']):
            score += 8
        
        # Score based on query term matches
        for term in query_terms:
            if len(term) > 2 and term in clean_lower:
                score += 3 if len(term) > 5 else 2
        
        # Bonus for list items and technical specs
        if clean_line.startswith('- ') and any(char in clean_line for char in [':', '**', 'v', '(', ')']):
            score += 2
            
        if score > 0:
            scored_lines.append((score, clean_line))
    
    # Sort by score and take top results
    scored_lines.sort(reverse=True, key=lambda x: x[0])
    relevant_lines = [line for score, line in scored_lines[:8]]
    
    return relevant_lines

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
    """Search through indexed documents using FAISS vector similarity with improved multi-chunk aggregation"""
    try:
        # Load FAISS index and metadata
        index = faiss.read_index('faiss_index.index')
        with open('faiss_index_metadata.pkl', 'rb') as f:
            metadata = pickle.load(f)
            chunks = metadata['chunks']
        
        # Load the model for encoding the query
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Expand query with synonyms
        expanded_terms = expand_query_terms(query)
        
        # Encode the query
        query_embedding = model.encode([query])
        
        # Search for similar documents with increased k for better coverage
        k = 15
        distances, indices = index.search(query_embedding.astype('float32'), k)
        
        # Create results with chunks and similarity scores
        top_results = []
        query_lower = query.lower()
        
        # Enhanced relevance scoring
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(chunks):
                chunk = chunks[idx]
                content_lower = chunk['content'].lower()
                section_title_lower = chunk.get('section_title', '').lower()
                doc_title_lower = chunk.get('document_title', '').lower()
                
                relevance_boost = 0
                
                # Enhanced ML/Technology stack detection
                ml_terms = ['machine learning', 'ml', 'ai', 'artificial intelligence', 'technology stack', 'tech stack']
                if any(term in query_lower for term in ml_terms):
                    if any(term in section_title_lower for term in ['machine learning', 'embedding', 'vector', 'nlp', 'language model']):
                        relevance_boost += 15
                    if 'technology stack' in doc_title_lower:
                        relevance_boost += 12
                    if any(term in content_lower for term in ['faiss', 'openai', 'transformers', 'pytorch']):
                        relevance_boost += 8
                
                # People/team queries
                people_terms = ['who is', 'cto', 'cio', 'team', 'lead', 'manager']
                if any(term in query_lower for term in people_terms):
                    if any(term in section_title_lower for term in ['cto', 'cio', 'lead', 'manager', 'team']):
                        relevance_boost += 15
                    if 'people' in doc_title_lower or 'team' in doc_title_lower:
                        relevance_boost += 10
                
                # General enhanced term matching with expanded terms
                for term in expanded_terms:
                    if len(term) > 2:
                        # Higher boost for exact section title matches
                        if term in section_title_lower:
                            relevance_boost += 5
                        # Medium boost for document title matches
                        if term in doc_title_lower:
                            relevance_boost += 3
                        # Lower boost for content matches
                        if term in content_lower:
                            relevance_boost += 1
                
                # Combine distance score with relevance boost
                base_score = float(1 / (1 + dist))
                final_score = base_score * (1 + relevance_boost * 0.3)
                
                top_results.append({
                    'chunk': chunk,
                    'score': final_score,
                    'distance': dist,
                    'relevance_boost': relevance_boost
                })
        
        # Re-sort by combined score
        top_results.sort(key=lambda x: x['score'], reverse=True)
        top_results = top_results[:8]
        
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
    
    # Enhanced multi-chunk aggregation
    sources = []
    seen_docs = set()
    
    # Group chunks by document and combine related content
    doc_chunks = {}
    for result in top_results:
        chunk = result['chunk']
        doc_title = chunk['document_title']
        
        if doc_title not in doc_chunks:
            doc_chunks[doc_title] = []
        doc_chunks[doc_title].append({
            'chunk': chunk,
            'score': result['score'],
            'relevance_boost': result['relevance_boost']
        })
    
    # Smart document selection and content aggregation
    query_lower_normalized = query.lower()
    selected_content = ""
    main_doc_title = ""
    
    # Enhanced query categorization
    ml_terms = ['machine learning', 'ml', 'ai', 'technology stack', 'tech stack', 'embedding', 'vector', 'model']
    people_terms = ['who is', 'cto', 'cio', 'team', 'lead', 'manager', 'responsibility']
    
    if any(term in query_lower_normalized for term in ml_terms):
        # For ML/tech queries, aggregate multiple related chunks
        tech_chunks = []
        for doc_title, chunks_list in doc_chunks.items():
            if 'Technology Stack' in doc_title:
                # Sort chunks by relevance and take top ones
                chunks_list.sort(key=lambda x: x['score'], reverse=True)
                tech_chunks.extend([c['chunk'] for c in chunks_list[:4]])  # Take top 4 chunks
                main_doc_title = doc_title
                break
        
        if tech_chunks:
            # Combine content from multiple related chunks
            combined_content = "\n\n".join([chunk['content'] for chunk in tech_chunks])
            selected_content = combined_content
        else:
            # Fallback to best single chunk
            best_doc = max(doc_chunks.items(), key=lambda x: max(c['score'] for c in x[1]))
            main_doc_title, chunks_list = best_doc
            selected_content = chunks_list[0]['chunk']['content']
    
    elif any(term in query_lower_normalized for term in people_terms):
        # For people queries, look for team/people documents
        people_chunks = []
        for doc_title, chunks_list in doc_chunks.items():
            if 'People' in doc_title or 'Team' in doc_title:
                chunks_list.sort(key=lambda x: x['score'], reverse=True)
                people_chunks.extend([c['chunk'] for c in chunks_list[:3]])
                main_doc_title = doc_title
                break
        
        if people_chunks:
            combined_content = "\n\n".join([chunk['content'] for chunk in people_chunks])
            selected_content = combined_content
        else:
            # Fallback
            best_doc = max(doc_chunks.items(), key=lambda x: max(c['score'] for c in x[1]))
            main_doc_title, chunks_list = best_doc
            selected_content = chunks_list[0]['chunk']['content']
    
    else:
        # General queries - take the best document
        best_doc = max(doc_chunks.items(), key=lambda x: max(c['score'] for c in x[1]))
        main_doc_title, chunks_list = best_doc
        # Potentially combine top 2 chunks if they're closely related
        chunks_list.sort(key=lambda x: x['score'], reverse=True)
        if len(chunks_list) > 1 and chunks_list[1]['score'] > chunks_list[0]['score'] * 0.7:
            selected_content = chunks_list[0]['chunk']['content'] + "\n\n" + chunks_list[1]['chunk']['content']
        else:
            selected_content = chunks_list[0]['chunk']['content']
    
    # Create response with improved extraction
    response_title = format_response_title(query)
    key_info = extract_relevant_info(selected_content, query)
    
    if key_info:
        formatted_info = '\\n'.join(key_info)
        message = f"{response_title}\\n{formatted_info}"
    else:
        # Handle special cases with better fallbacks
        query_lower = query.lower()
        if 'ceo' in query_lower:
            message = "## CEO Information\\n\\nNo CEO information is available in the current documentation.\\n\\nAvailable executives:\\n• Chief Technology Officer (CTO): Alexandra Chen\\n• Chief Information Officer (CIO): Marcus Williams"
        elif 'who is' in query_lower:
            person = query.replace('Who is', '').replace('?', '').strip()
            message = f"## {person}\\n\\nNo information found about {person} in the documentation."
        else:
            # Provide a snippet of the most relevant content
            content_preview = selected_content[:300] + "..." if len(selected_content) > 300 else selected_content
            message = f"## {response_title.replace('##', '').strip()}\\n\\n{content_preview}"
    
    # Create source references
    for doc_title in [main_doc_title]:
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