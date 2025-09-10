import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, MessageSquare, Users, Zap, Target, Wrench, BookOpen } from 'lucide-react'
import { Message } from './Message'
import { MessageInput } from './MessageInput'
import { Logo } from './Logo'
import { useChatStore } from '@/store/chat'

export function ChatInterface() {
  const { currentChat, error, clearError } = useChatStore()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [suggestedQuery, setSuggestedQuery] = useState<string | null>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [currentChat?.messages])

  const welcomeCards = [
    {
      icon: BookOpen,
      title: 'Application Architecture',
      description: 'System design and components',
      query: 'Tell me about the application architecture'
    },
    {
      icon: Zap,
      title: 'Technology Stack',
      description: 'Languages, frameworks, and tools',
      query: 'What is the technology stack?'
    },
    {
      icon: Target,
      title: 'Deployment Strategies',
      description: 'CI/CD and release processes',
      query: 'Show me deployment strategies'
    },
    {
      icon: Users,
      title: 'Team Members',
      description: 'People and organizational structure',
      query: 'Who are the team members?'
    },
    {
      icon: MessageSquare,
      title: 'User Journey',
      description: 'User experience and workflows',
      query: 'Explain the user journey'
    },
    {
      icon: Wrench,
      title: 'Maintenance Procedures',
      description: 'Housekeeping and operations',
      query: 'What are the maintenance procedures?'
    }
  ]

  const WelcomeScreen = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center justify-center min-h-full p-6"
    >
      <div className="text-center max-w-4xl mx-auto">
        {/* Hero Section */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-12"
        >
          <div className="flex justify-center mb-6">
            <Logo size="large" animate />
          </div>
          
          <motion.h1
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-4xl font-bold mb-4 gradient-text"
          >
            Welcome to WhoKnows?
          </motion.h1>
          
          <motion.p
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto leading-relaxed"
          >
            Your intelligent enterprise knowledge assistant. Ask me anything about 
            documentation, team members, technology stack, or processes.
          </motion.p>
        </motion.div>

        {/* Quick Actions Grid */}
        <motion.div
          initial={{ y: 40, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8"
        >
          {welcomeCards.map((card, index) => (
            <motion.button
              key={card.title}
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.6 + index * 0.1 }}
              whileHover={{ 
                scale: 1.05, 
                y: -5,
                transition: { duration: 0.2 }
              }}
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                setSuggestedQuery(card.query)
              }}
              className="group p-6 glass glass-border rounded-2xl text-left hover:shadow-xl transition-all duration-300"
            >
              <div className="flex items-start space-x-4">
                <motion.div
                  whileHover={{ rotate: 360 }}
                  transition={{ duration: 0.6 }}
                  className="w-12 h-12 rounded-xl flex items-center justify-center bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 shadow-sm"
                >
                  <card.icon size={24} />
                </motion.div>
                
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-gray-700 dark:group-hover:text-gray-300 transition-colors">
                    {card.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                    {card.description}
                  </p>
                </div>
              </div>
            </motion.button>
          ))}
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ y: 40, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-center"
        >
          <div className="inline-flex items-center space-x-6 px-6 py-3 glass glass-border rounded-full">
            <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
              <div className="w-2 h-2 bg-gray-600 dark:bg-gray-400 rounded-full animate-pulse" />
              <span>AI-Powered</span>
            </div>
            <div className="w-px h-4 bg-gray-300 dark:bg-gray-600" />
            <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
              <div className="w-2 h-2 bg-gray-600 dark:bg-gray-400 rounded-full animate-pulse animation-delay-100" />
              <span>Real-time</span>
            </div>
            <div className="w-px h-4 bg-gray-300 dark:bg-gray-600" />
            <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
              <div className="w-2 h-2 bg-gray-600 dark:bg-gray-400 rounded-full animate-pulse animation-delay-200" />
              <span>Secure</span>
            </div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  )

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Error Banner */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800 px-6 py-3"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <AlertCircle size={20} className="text-red-600 dark:text-red-400" />
                <span className="text-red-800 dark:text-red-200 text-sm font-medium">
                  {error}
                </span>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={clearError}
                className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200 text-sm font-medium"
              >
                Dismiss
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Messages Container */}
      <div 
        ref={containerRef}
        className="flex-1 overflow-y-auto scrollbar-thin p-6"
      >
        <div className="max-w-4xl mx-auto">
          <AnimatePresence mode="wait">
            {!currentChat || currentChat.messages.length === 0 ? (
              <WelcomeScreen key="welcome" />
            ) : (
              <motion.div
                key="messages"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-6"
              >
                {currentChat.messages.map((message, index) => (
                  <Message
                    key={message.id}
                    message={message}
                    isLatest={index === currentChat.messages.length - 1}
                  />
                ))}
                <div ref={messagesEndRef} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Input Area */}
      <MessageInput 
        suggestedQuery={suggestedQuery}
        onQueryProcessed={() => setSuggestedQuery(null)}
      />
    </div>
  )
}

