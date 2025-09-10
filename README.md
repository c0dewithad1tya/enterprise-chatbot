# WhoKnows? - Your Intelligent Knowledge Assistant

A modern, AI-powered chatbot that provides intelligent access to organizational knowledge through semantic search and natural language processing. Built with cutting-edge technologies for an exceptional user experience.

## Features

- 🔍 **Semantic Search** - Uses FAISS vector embeddings for accurate document retrieval
- 💬 **Intelligent Chat Interface** - Advanced conversational AI with typing animations and real-time responses
- 🎨 **Modern Design** - Minimal dark grey and white theme with glass morphism effects
- 📱 **Responsive UI** - Mobile-first design that works perfectly on all devices
- ⚡ **Lightning Fast** - Built with Vite for instant hot-reloads and optimized performance
- 🔄 **Real-time Updates** - Live chat updates with smooth animations using Framer Motion
- 💾 **Persistent History** - Chat conversations are saved locally with automatic management
- 🌙 **Theme Support** - Light/dark mode with system preference detection
- ♿ **Accessibility First** - Full ARIA support and keyboard navigation
- 📚 **Smart Suggestions** - Context-aware quick action cards for common queries

## Tech Stack

### Frontend (Modern React App)
- **React 18** with TypeScript for type-safe, performant UI
- **Vite** - Lightning-fast build tool and dev server
- **Framer Motion** - Advanced animations and micro-interactions
- **Tailwind CSS** - Utility-first CSS with custom design system
- **Zustand** - Lightweight state management with persistence
- **React Query (TanStack Query)** - Data fetching, caching, and synchronization
- **React Hook Form** - Performant form handling with validation
- **React Markdown** - Rich markdown rendering with syntax highlighting
- **Lucide React** - Beautiful, customizable icons

### Backend
- **Python 3.11** with Flask
- **Sentence-BERT** for embeddings
- **FAISS** for vector similarity search
- **LangChain** for NLP processing

### Development Tools
- **TypeScript** - Static typing for better developer experience
- **ESLint** - Code linting and formatting
- **PostCSS** - CSS processing and optimization

## Quick Start

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

3. Start the Flask backend:
```bash
python chatbot-backend.py
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

## Project Structure

```
chatbot/
├── src/                        # React TypeScript source code
│   ├── components/             # Reusable UI components
│   │   ├── ChatInterface.tsx   # Main chat interface with welcome screen
│   │   ├── Message.tsx         # Individual message component with animations
│   │   ├── MessageInput.tsx    # Advanced input with suggestions and voice
│   │   ├── Sidebar.tsx         # Collapsible sidebar with chat history
│   │   ├── Header.tsx          # Application header with controls
│   │   └── ErrorBoundary.tsx   # Error handling component
│   ├── store/                  # State management
│   │   ├── chat.ts             # Chat state and history management
│   │   └── settings.ts         # App settings and theme management
│   ├── services/               # External service integrations
│   │   └── api.ts              # Backend API communication
│   ├── lib/                    # Utility functions
│   │   └── utils.ts            # Common utilities and helpers
│   ├── types/                  # TypeScript type definitions
│   │   └── index.ts            # Application types and interfaces
│   ├── App.tsx                 # Main application component
│   ├── main.tsx                # Application entry point
│   └── index.css               # Global styles and Tailwind imports
├── chatbot-backend.py          # Flask backend with API endpoints
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

## API Endpoints

- `POST /api/chat` - Process user queries and return AI responses
- `GET /api/health` - Health check endpoint
- **CORS enabled** for cross-origin requests from React app

## Development Scripts

```bash
# Frontend development
npm run dev          # Start Vite dev server with hot reload
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint for code quality

# Backend development
python chatbot-backend.py  # Start Flask development server
```

## Features in Detail

### Chat Interface
- **Welcome Screen**: Interactive cards for common queries
- **Typing Animation**: Real-time typing effect for AI responses
- **Message History**: Persistent chat history with automatic cleanup
- **Error Handling**: Graceful error handling with retry mechanisms
- **Loading States**: Smooth loading animations and status indicators

### Advanced Input
- **Auto-resize**: Textarea automatically adjusts height
- **Character Counter**: Shows when approaching limits
- **Suggested Questions**: Context-aware quick suggestions
- **Keyboard Shortcuts**: Enter to send, Shift+Enter for new line
- **Voice Recording**: Ready for future voice input integration

### Responsive Design
- **Mobile-first**: Optimized for all screen sizes
- **Touch-friendly**: Large touch targets and smooth gestures
- **Performance**: Lazy loading and code splitting for fast load times
- **Accessibility**: Full keyboard navigation and screen reader support

## Documentation

The system indexes markdown files from the `documentation/` folder:
- Application Architecture
- Technology Stack  
- Deployment Strategies
- Team Information
- User Journeys
- Maintenance Procedures

## Contributing

This project follows modern React development best practices:
- TypeScript for type safety
- Component composition patterns
- Custom hooks for reusable logic
- Proper error boundaries
- Performance optimizations

## License

Internal use only - Enterprise proprietary