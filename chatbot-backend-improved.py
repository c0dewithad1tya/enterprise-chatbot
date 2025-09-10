"""
WhoKnows? Chatbot Backend - Enhanced Version
============================================
Uses the new search engine for better document retrieval and presentation
"""

import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from search_engine import SearchEngine, keyword_search

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize search engine
search_engine = SearchEngine()
search_initialized = search_engine.initialize()

if search_initialized:
    logger.info("Search engine initialized successfully with vector index")
else:
    logger.warning("Vector search not available, falling back to keyword search")


@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint with improved search"""
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        if search_initialized:
            # Use the enhanced search engine
            result = search_engine.search(query)
        else:
            # Fallback to keyword search
            result = keyword_search(query)
        
        # Log query and response quality
        logger.info(f"Query: {query}")
        if 'query_analysis' in result:
            logger.info(f"Query type: {result['query_analysis']['type']}")
            logger.info(f"Key terms: {result['query_analysis']['key_terms']}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An error occurred while processing your request.'
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'search_engine': 'initialized' if search_initialized else 'fallback mode'
    })


@app.route('/api/reindex', methods=['POST'])
def reindex():
    """Trigger reindexing of documents"""
    global search_engine, search_initialized
    
    try:
        # Reinitialize the search engine
        search_engine = SearchEngine()
        search_initialized = search_engine.initialize()
        
        if search_initialized:
            return jsonify({
                'status': 'success',
                'message': 'Search index reloaded successfully'
            })
        else:
            return jsonify({
                'status': 'partial',
                'message': 'Index reload failed, using keyword search'
            })
            
    except Exception as e:
        logger.error(f"Error reindexing: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def stats():
    """Get search engine statistics"""
    stats_data = {
        'search_mode': 'vector' if search_initialized else 'keyword',
        'index_loaded': search_initialized
    }
    
    if search_initialized and search_engine.chunks:
        stats_data.update({
            'total_chunks': len(search_engine.chunks),
            'total_documents': len(set(c['document_title'] for c in search_engine.chunks))
        })
    
    return jsonify(stats_data)


if __name__ == '__main__':
    print("=" * 60)
    print("WhoKnows? Chatbot Backend - Enhanced Version")
    print("=" * 60)
    print(f"Search Mode: {'Vector Search' if search_initialized else 'Keyword Fallback'}")
    print("Starting server on http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, port=5000)