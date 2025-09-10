# WhoKnows? - Your Intelligent Enterprise Knowledge Assistant

A modern, AI-powered chatbot that provides intelligent access to organizational knowledge through advanced semantic search, query intent understanding, and natural language processing. Built with cutting-edge technologies for an exceptional user experience.

## 🚀 Recent Major Improvements

### Enhanced Search Engine
- **Query Intent Understanding** - Classifies queries (person, technology, process, architecture)
- **Intelligent Ranking** - Context-aware scoring based on query type
- **Smart Content Extraction** - Extracts structured data, key-value pairs, and lists
- **Clean Text Formatting** - Removes markdown artifacts and escape characters
- **2000 Character Limit** - Optimized content length for readability
- **Document Links** - Direct links to full documentation when content is truncated
- **Confidence Scoring** - Visual indicators showing search result confidence levels

### AI-Powered Features
- **Smart Summarization** - Intelligent content summarization with context awareness
- **Conversational Memory** - 2-message context window for better continuity
- **Toggle Modes** - Switch between brief summaries and detailed responses
- **Confidence Indicators** - High/Medium/Low confidence badges with explanations

### UI/UX Enhancements
- **Unified Logo Design** - Consistent minimal grey/white theme across all components
- **Improved Result Display** - Cleaner, more readable search results
- **Source Attribution** - Shows relevance scores and document sources
- **Better Message Rendering** - Enhanced markdown display with proper formatting
- **Redesigned Sidebar** - Improved collapsed state with better icon placement
- **Visual Confidence Badges** - Color-coded indicators with percentage scores

## ✨ Features

- 🧠 **Intelligent Search** - Advanced query analysis with intent understanding
- 🔍 **Semantic Search** - Uses FAISS vector embeddings for accurate document retrieval
- 💬 **Smart Chat Interface** - Context-aware responses with typing animations
- 📊 **Confidence Scores** - Visual indicators showing response reliability (High/Medium/Low)
- 📝 **AI Summarization** - Intelligent content summarization with toggle modes
- 🧩 **Conversational Context** - Maintains 2-message context for better continuity
- 🎨 **Modern Minimal Design** - Clean grey and white theme with glass morphism effects
- 📱 **Responsive UI** - Mobile-first design that works perfectly on all devices
- ⚡ **Lightning Fast** - Built with Vite for instant hot-reloads and optimized performance
- 🔄 **Real-time Updates** - Live chat updates with smooth animations using Framer Motion
- 💾 **Persistent History** - Chat conversations are saved locally with automatic management
- 🌙 **Theme Support** - Light/dark mode with system preference detection
- ♿ **Accessibility First** - Full ARIA support and keyboard navigation
- 📚 **Smart Suggestions** - Context-aware quick action cards for common queries
- 📄 **Document References** - View full documentation with source links

## 🛠️ Tech Stack

### Frontend (Modern React App)
- **React 18** with TypeScript for type-safe, performant UI
- **Vite** - Lightning-fast build tool and dev server
- **Framer Motion** - Advanced animations and micro-interactions
- **Tailwind CSS** - Utility-first CSS with custom design system
- **Zustand** - Lightweight state management with persistence
- **React Query (TanStack Query)** - Data fetching, caching, and synchronization
- **React Markdown** - Rich markdown rendering with syntax highlighting
- **Lucide React** - Beautiful, customizable icons

### Backend
- **Python 3.11** with Flask
- **Custom Search Engine** - Advanced query analysis with confidence scoring
- **AI Summarization** - Smart extraction and content summarization
- **Sentence-BERT** for embeddings (all-MiniLM-L6-v2)
- **FAISS** for vector similarity search
- **Smart Content Processing** - Automatic cleaning and formatting
- **Conversational Context** - Maintains conversation history for continuity

### Development Tools
- **TypeScript** - Static typing for better developer experience
- **ESLint** - Code linting and formatting
- **PostCSS** - CSS processing and optimization

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Index your documents:
```bash
python index_documents_improved.py
python create_vector_index.py
```

3. Start the improved Flask backend:
```bash
python chatbot-backend-improved.py
```
Backend will run on `http://localhost:5000`

### Frontend Setup

4. Install Node.js dependencies:
```bash
npm install
```

5. Start the development server:
```bash
npm run dev
```
Frontend will run on `http://localhost:3000`

## 📁 Project Structure

```
chatbot/
├── src/                        # React TypeScript source code
│   ├── components/             # Reusable UI components
│   │   ├── ChatInterface.tsx   # Main chat interface with welcome screen
│   │   ├── Message.tsx         # Message component with confidence indicators
│   │   ├── MessageInput.tsx    # Advanced input with summary toggle
│   │   ├── Sidebar.tsx         # Redesigned collapsible sidebar
│   │   ├── Header.tsx          # Application header with controls
│   │   ├── Logo.tsx            # Unified logo component
│   │   └── ErrorBoundary.tsx   # Error handling component
│   ├── store/                  # State management
│   │   ├── chat.ts             # Chat state with context management
│   │   └── settings.ts         # App settings and theme management
│   ├── services/               # External service integrations
│   │   └── api.ts              # Backend API communication
│   ├── lib/                    # Utility functions
│   │   └── utils.ts            # Common utilities and helpers
│   ├── types/                  # TypeScript type definitions
│   │   └── index.ts            # Types including Confidence interface
│   ├── App.tsx                 # Main application component
│   ├── main.tsx                # Application entry point
│   └── index.css               # Global styles and Tailwind imports
├── chatbot-backend-improved.py # Enhanced Flask backend with confidence scoring
├── search_engine.py            # Advanced search with confidence calculation
├── summarizer.py               # AI-powered content summarization
├── create_vector_index.py      # FAISS index creation
├── index_documents_improved.py # Document indexing script
├── documentation/              # Markdown documentation files
├── faiss_index.*              # Vector index files
├── package.json               # Node.js dependencies and scripts
├── vite.config.ts             # Vite configuration
├── tailwind.config.js         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
└── requirements.txt           # Python dependencies
```

## 🔌 API Endpoints

- `POST /api/chat` - Process user queries with intelligent search
- `GET /api/health` - Health check endpoint with search engine status
- `POST /api/reindex` - Trigger document reindexing
- `GET /api/stats` - Get search engine statistics
- **CORS enabled** for cross-origin requests from React app

## 🎯 Search Engine Features

### Query Analysis
- **Intent Classification** - Identifies query type (person, technology, process, etc.)
- **Entity Extraction** - Extracts names, technologies, and roles
- **Term Expansion** - Expands queries with synonyms and related terms

### Content Processing
- **Structured Data Extraction** - Pulls out key-value pairs and lists
- **Smart Highlighting** - Generates contextual highlights
- **Clean Formatting** - Removes markdown artifacts and escape characters
- **Character Limits** - Enforces 2000 character limit for readability

### Ranking Algorithm
- **Context-Aware Scoring** - Different strategies for different query types
- **Exact Phrase Matching** - Boosts exact matches in titles and content
- **Relevance Penalties** - Reduces scores for irrelevant content
- **Multi-Document Aggregation** - Combines results from multiple sources

## 📝 Development Scripts

```bash
# Frontend development
npm run dev          # Start Vite dev server with hot reload
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint for code quality

# Backend development
python chatbot-backend-improved.py  # Start enhanced Flask server
python create_vector_index.py       # Rebuild search index
python index_documents_improved.py  # Re-index documents
```

## 🎨 Features in Detail

### Chat Interface
- **Welcome Screen**: Interactive cards for common queries
- **Clean Text Display**: Properly formatted responses without artifacts
- **Typing Animation**: Real-time typing effect for AI responses
- **Message History**: Persistent chat history with automatic cleanup
- **Source Links**: Direct links to documentation sources
- **Error Handling**: Graceful error handling with retry mechanisms

### Search Capabilities
- **Machine Learning Stack Queries**: Finds relevant ML/AI information
- **People & Team Queries**: Locates team members and responsibilities
- **Technology Queries**: Returns specific tech stack details
- **Process Queries**: Explains workflows and procedures

### Responsive Design
- **Mobile-first**: Optimized for all screen sizes
- **Touch-friendly**: Large touch targets and smooth gestures
- **Performance**: Lazy loading and code splitting for fast load times
- **Accessibility**: Full keyboard navigation and screen reader support

## 📚 Documentation

The system indexes markdown files from the `documentation/` folder:
- Application Architecture
- Technology Stack  
- Deployment Strategies
- People and Teams
- User Journeys
- Maintenance Procedures
- High-Level Flow

## 🔧 Configuration

### Search Engine Settings
- **Max Results**: 5 aggregated results per query
- **Character Limit**: 2000 characters per response
- **Vector Dimensions**: 384 (all-MiniLM-L6-v2)
- **Index Type**: FAISS IndexFlatL2

### Frontend Settings
- **Theme**: Light/Dark/System
- **Chat History**: Stored in localStorage
- **Max Message Length**: 1000 characters

## 🤝 Contributing

This project follows modern development best practices:
- TypeScript for type safety
- Component composition patterns
- Custom hooks for reusable logic
- Proper error boundaries
- Performance optimizations
- Clean code architecture

## 📈 Performance

- **Search Latency**: < 100ms for vector search
- **Frontend Load Time**: < 2s initial load
- **Hot Reload**: Instant with Vite
- **Memory Usage**: Optimized with React memoization

## 🔒 Security

- Input sanitization for all user queries
- CORS configuration for API security
- No credential storage in code
- Secure markdown rendering

## 📄 License

Internal use only - Enterprise proprietary

---

**Built with ❤️ using modern web technologies**