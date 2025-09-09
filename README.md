# WhoKnows? - Your Intelligent Knowledge Assistant

A modern, AI-powered chatbot that provides intelligent access to organizational knowledge through semantic search and natural language processing. When you need answers, ask WhoKnows?

## Features

- 🔍 **Semantic Search** - Uses FAISS vector embeddings for accurate document retrieval
- 💬 **Natural Language Interface** - Chat-based interaction with markdown support
- 🎨 **Modern UI** - Clean, responsive design with light/dark theme support
- 📚 **Document Management** - Indexes and searches through markdown documentation
- ⚡ **Fast Response** - Optimized vector similarity search for quick results

## Tech Stack

- **Backend**: Python 3.11, Flask
- **ML/NLP**: Sentence-BERT, FAISS, LangChain
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: Vector embeddings with FAISS
- **Markdown**: Marked.js for rendering

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Index your documents:
```bash
python index_documents.py
python create_vector_index.py
```

3. Start the backend:
```bash
python chatbot-backend.py
```

4. Open the chatbot:
```bash
start chatbot-modern.html
```

## Project Structure

```
chatbot/
├── chatbot-backend.py      # Flask backend with API endpoints
├── chatbot-modern.html     # Modern UI interface
├── create_vector_index.py  # FAISS index creation
├── index_documents.py      # Document indexing script
├── themes.py              # Theme management system
├── documentation/         # Markdown documentation files
├── faiss_index.*         # Vector index files
└── requirements.txt      # Python dependencies
```

## API Endpoints

- `POST /api/chat` - Process user queries
- `GET /api/themes` - Get available themes
- `GET /api/health` - Health check

## Usage

1. Open `chatbot-modern.html` in your browser
2. Type your question in the chat interface
3. Get instant responses with source citations
4. Toggle between light/dark themes

## Documentation

The system indexes markdown files from the `documentation/` folder:
- Application Architecture
- Technology Stack
- Deployment Strategies
- Team Information
- User Journeys
- Maintenance Procedures

## License

Internal use only - Enterprise proprietary