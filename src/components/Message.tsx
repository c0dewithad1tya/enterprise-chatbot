import React, { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Copy, Check, FileText, ExternalLink, User, Bot } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import type { Message as MessageType } from '@/types'
import { copyToClipboard, formatTimestamp, cn } from '@/lib/utils'

interface MessageProps {
  message: MessageType
  isLatest?: boolean
}

export const Message = React.memo<MessageProps>(function Message({ message, isLatest }) {
  const [copied, setCopied] = useState(false)
  const [displayedContent, setDisplayedContent] = useState('')
  const [isTyping, setIsTyping] = useState(false)

  const isUser = message.type === 'user'
  const isLoading = message.isLoading

  // Typing animation for assistant messages
  useEffect(() => {
    if (isUser || !isLatest || isLoading) {
      setDisplayedContent(message.content)
      setIsTyping(false)
      return
    }

    if (message.content && message.content !== displayedContent) {
      setIsTyping(true)
      let index = 0
      const content = message.content

      const interval = setInterval(() => {
        if (index < content.length) {
          setDisplayedContent(content.slice(0, index + 1))
          index++
        } else {
          setIsTyping(false)
          clearInterval(interval)
        }
      }, 20)

      return () => clearInterval(interval)
    }
  }, [message.content, isUser, isLatest, isLoading])

  const handleCopy = async () => {
    const success = await copyToClipboard(message.content)
    if (success) {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const renderMarkdown = useMemo(() => (content: string) => (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ node, inline, className, children, ...props }: any) {
          const match = /language-(\w+)/.exec(className || '')
          const language = match?.[1] || 'text'
          
          return !inline && match ? (
            <SyntaxHighlighter
              style={oneDark as any}
              language={language}
              PreTag="div"
              className="rounded-lg !bg-gray-900 dark:!bg-gray-950"
              {...props}
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          ) : (
            <code 
              className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-sm font-mono"
              {...props}
            >
              {children}
            </code>
          )
        },
        h1: ({ children }) => (
          <h1 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
            {children}
          </h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">
            {children}
          </h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-lg font-medium mb-2 text-gray-900 dark:text-white">
            {children}
          </h3>
        ),
        p: ({ children }) => (
          <p className="mb-3 leading-relaxed text-gray-800 dark:text-gray-200">
            {children}
          </p>
        ),
        ul: ({ children }) => (
          <ul className="list-disc list-inside mb-3 space-y-1 text-gray-800 dark:text-gray-200">
            {children}
          </ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal list-inside mb-3 space-y-1 text-gray-800 dark:text-gray-200">
            {children}
          </ol>
        ),
        li: ({ children }) => (
          <li className="ml-2">{children}</li>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-primary-500 pl-4 italic mb-3 text-gray-700 dark:text-gray-300">
            {children}
          </blockquote>
        ),
        a: ({ href, children }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-600 dark:text-primary-400 hover:underline inline-flex items-center gap-1"
          >
            {children}
            <ExternalLink size={12} />
          </a>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  ), [])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn(
        'flex mb-6 group',
        isUser ? 'justify-end' : 'justify-start'
      )}
      role="article"
      aria-label={`${isUser ? 'Your' : 'Assistant'} message`}
    >
      <div className={cn(
        'flex items-start space-x-3 max-w-4xl',
        isUser ? 'flex-row-reverse space-x-reverse' : ''
      )}>
        {/* Avatar */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.1 }}
          className={cn(
            'w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0 shadow-sm',
            isUser 
              ? 'bg-gray-700 dark:bg-gray-300 text-white dark:text-gray-900' 
              : 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
          )}
          role="img"
          aria-label={isUser ? 'User avatar' : 'Assistant avatar'}
        >
          {isUser ? <User size={16} aria-hidden="true" /> : <Bot size={16} aria-hidden="true" />}
        </motion.div>

        {/* Message Content */}
        <div 
          className={cn(
            'rounded-2xl px-4 py-3 shadow-sm',
            isUser
              ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
              : 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800'
          )}
          role="region"
          aria-label="Message content"
        >
          {/* Loading State */}
          {isLoading ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center space-x-2 text-gray-600 dark:text-gray-400"
              role="status"
              aria-live="polite"
              aria-label="Assistant is thinking"
            >
              <motion.div
                animate={{ opacity: [1, 0.5, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="flex space-x-1"
                aria-hidden="true"
              >
                <div className="w-2 h-2 bg-primary-500 rounded-full" />
                <div className="w-2 h-2 bg-primary-500 rounded-full animation-delay-100" />
                <div className="w-2 h-2 bg-primary-500 rounded-full animation-delay-200" />
              </motion.div>
              <span className="text-sm">Thinking...</span>
            </motion.div>
          ) : (
            <div className="message-content">
              {isUser ? (
                <p className="whitespace-pre-wrap" role="text">{message.content}</p>
              ) : (
                <div className="prose prose-sm max-w-none dark:prose-invert" role="text">
                  {renderMarkdown(displayedContent.replace(/\\n/g, '\n').replace(/\\t/g, '  '))}
                  {isTyping && (
                    <motion.span
                      animate={{ opacity: [0, 1, 0] }}
                      transition={{ duration: 1, repeat: Infinity }}
                      className="inline-block w-2 h-4 bg-primary-500 ml-1"
                      role="status"
                      aria-label="Assistant is typing"
                    />
                  )}
                </div>
              )}

              {/* Sources */}
              {message.sources && message.sources.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-600"
                >
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                    <FileText size={14} />
                    Sources:
                  </p>
                  <div className="space-y-1">
                    {message.sources.map((source, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 * index }}
                        className="flex items-center space-x-2 text-sm"
                      >
                        <div className="w-1.5 h-1.5 bg-primary-500 rounded-full" />
                        {source.link ? (
                          <a
                            href={source.link}
                            className="text-primary-600 dark:text-primary-400 hover:underline inline-flex items-center gap-1"
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {source.title}
                            <ExternalLink size={10} />
                          </a>
                        ) : (
                          <span className="text-primary-600 dark:text-primary-400">
                            {source.title}
                          </span>
                        )}
                        {source.relevance && (
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            ({Math.round(source.relevance * 100)}% match)
                          </span>
                        )}
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Message Actions */}
              {!isUser && !isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5 }}
                  className="flex items-center justify-between mt-3 pt-2 border-t border-gray-100 dark:border-gray-700"
                >
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {formatTimestamp(message.timestamp)}
                  </span>
                  
                  <div className="flex items-center space-x-2">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={handleCopy}
                      className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                      title="Copy message"
                      aria-label={copied ? 'Message copied' : 'Copy message to clipboard'}
                    >
                      <AnimatePresence mode="wait">
                        {copied ? (
                          <motion.div
                            key="checked"
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            exit={{ scale: 0 }}
                          >
                            <Check size={14} className="text-green-600" />
                          </motion.div>
                        ) : (
                          <motion.div
                            key="copy"
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            exit={{ scale: 0 }}
                          >
                            <Copy size={14} className="text-gray-500 dark:text-gray-400" />
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.button>
                  </div>
                </motion.div>
              )}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
})