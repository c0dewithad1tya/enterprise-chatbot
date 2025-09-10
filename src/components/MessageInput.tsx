import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Paperclip, Loader2, Mic, MicOff } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { useMutation } from '@tanstack/react-query'
import { apiService } from '@/services/api'
import { useChatStore } from '@/store/chat'
import { cn } from '@/lib/utils'

interface MessageForm {
  message: string
}

export function MessageInput() {
  const [isRecording, setIsRecording] = useState(false)
  const [charCount, setCharCount] = useState(0)
  const [loadingMessageId, setLoadingMessageId] = useState<string | null>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  
  const { addMessage, updateMessage, setLoading, setError, clearError, currentChat } = useChatStore()
  
  const { register, handleSubmit, reset, watch, setValue } = useForm<MessageForm>({
    defaultValues: { message: '' }
  })
  
  const messageValue = watch('message')
  
  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`
    }
    setCharCount(messageValue?.length || 0)
  }, [messageValue])

  const sendMessageMutation = useMutation({
    mutationFn: (query: string) => apiService.sendMessage(query),
    onMutate: async (query: string) => {
      clearError()
      setLoading(true)
      
      // Add user message immediately
      addMessage({
        type: 'user',
        content: query,
      })
      
      // Add loading assistant message and store its ID
      const loadingMessage = {
        type: 'assistant' as const,
        content: '',
        isLoading: true,
      }
      
      // We'll use a temporary ID that gets generated in the store
      addMessage(loadingMessage)
      
      // Since we can't get the ID directly from addMessage, we'll track it differently
      // The loading message will be the last assistant message
      return { query }
    },
    onSuccess: (data, variables, context) => {
      // Get the current chat to find the loading message
      const currentChat = useChatStore.getState().currentChat
      if (currentChat && currentChat.messages.length > 0) {
        // Find the last message that is loading
        const lastMessage = currentChat.messages[currentChat.messages.length - 1]
        
        if (lastMessage.type === 'assistant' && lastMessage.isLoading) {
          // Update the loading message with the real response
          updateMessage(lastMessage.id, {
            content: data.message,
            sources: data.sources,
            isLoading: false,
          })
        }
      }
    },
    onError: (error: any) => {
      // Get the current chat to remove the loading message on error
      const currentChat = useChatStore.getState().currentChat
      if (currentChat && currentChat.messages.length > 0) {
        const lastMessage = currentChat.messages[currentChat.messages.length - 1]
        
        if (lastMessage.type === 'assistant' && lastMessage.isLoading) {
          // Update the loading message to show error
          updateMessage(lastMessage.id, {
            content: 'Sorry, I encountered an error while processing your request.',
            isLoading: false,
          })
        }
      }
      
      setError(error.message || 'Failed to send message')
      console.error('Send message error:', error)
    },
    onSettled: () => {
      setLoading(false)
    },
  })

  const onSubmit = (data: MessageForm) => {
    const message = data.message.trim()
    if (!message || sendMessageMutation.isPending) return
    
    sendMessageMutation.mutate(message)
    reset()
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(onSubmit)()
    }
  }

  const suggestedQuestions = [
    "Who is the CTO?",
    "What is the machine learning stack?",
    "Tell me about deployment strategies",
    "Show me the team structure"
  ]

  const handleSuggestionClick = (question: string) => {
    setValue('message', question)
    setTimeout(() => handleSubmit(onSubmit)(), 100)
  }

  const toggleRecording = () => {
    setIsRecording(!isRecording)
    // TODO: Implement voice recording functionality
  }

  return (
    <motion.div
      initial={{ y: 50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="p-6 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800"
    >
      <div className="max-w-4xl mx-auto space-y-4">
        {/* Suggested Questions */}
        <AnimatePresence>
          {!messageValue && (!currentChat || currentChat.messages.length === 0) && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex flex-wrap gap-2 justify-center"
            >
              {suggestedQuestions.map((question, index) => (
                <motion.button
                  key={question}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleSuggestionClick(question)}
                  className="px-4 py-2 text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full hover:border-primary-300 dark:hover:border-primary-600 transition-all duration-200 shadow-sm hover:shadow-md"
                >
                  {question}
                </motion.button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Input Container */}
        <motion.div
          whileHover={{ y: -2 }}
          className={cn(
            'relative bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700',
            'shadow-sm hover:shadow-md transition-all duration-200',
            'focus-within:ring-1 focus-within:ring-gray-400 focus-within:border-gray-400'
          )}
        >
          <form onSubmit={handleSubmit(onSubmit)} className="flex items-end p-4">
            {/* Textarea */}
            <div className="flex-1 relative">
              <textarea
                {...register('message', { required: true, maxLength: 2000 })}
                ref={(e) => {
                  register('message').ref(e)
                  if (textareaRef.current !== e) {
                    (textareaRef as any).current = e
                  }
                }}
                placeholder="Message WhoKnows..."
                className="w-full resize-none bg-transparent border-none outline-none text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 text-base leading-6 max-h-40 min-h-[24px] py-2 pr-12"
                rows={1}
                onKeyPress={handleKeyPress}
                disabled={sendMessageMutation.isPending}
              />
              
              {/* Character count */}
              <AnimatePresence>
                {charCount > 100 && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute bottom-1 right-16 text-xs text-gray-400 dark:text-gray-500"
                  >
                    {charCount}/2000
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-2 ml-3">
              {/* Voice Recording Button */}
              <motion.button
                type="button"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={toggleRecording}
                className={cn(
                  'p-2 rounded-full transition-all duration-200',
                  isRecording
                    ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                    : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                )}
                title={isRecording ? "Stop recording" : "Start voice recording"}
                disabled={sendMessageMutation.isPending}
              >
                <AnimatePresence mode="wait">
                  {isRecording ? (
                    <motion.div
                      key="recording"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      exit={{ scale: 0 }}
                    >
                      <MicOff size={18} />
                    </motion.div>
                  ) : (
                    <motion.div
                      key="not-recording"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      exit={{ scale: 0 }}
                    >
                      <Mic size={18} />
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.button>

              {/* Attachment Button */}
              <motion.button
                type="button"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="Attach file (coming soon)"
                disabled
              >
                <Paperclip size={18} />
              </motion.button>

              {/* Send Button */}
              <motion.button
                type="submit"
                whileHover={{ scale: messageValue?.trim() ? 1.05 : 1 }}
                whileTap={{ scale: messageValue?.trim() ? 0.95 : 1 }}
                disabled={!messageValue?.trim() || sendMessageMutation.isPending}
                className={cn(
                  'p-2.5 rounded-full transition-all duration-200 shadow-sm',
                  messageValue?.trim() && !sendMessageMutation.isPending
                    ? 'bg-gray-900 dark:bg-gray-100 hover:bg-gray-800 dark:hover:bg-gray-200 text-white dark:text-gray-900'
                    : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                )}
                title="Send message"
              >
                <AnimatePresence mode="wait">
                  {sendMessageMutation.isPending ? (
                    <motion.div
                      key="loading"
                      initial={{ rotate: 0 }}
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    >
                      <Loader2 size={18} />
                    </motion.div>
                  ) : (
                    <motion.div
                      key="send"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      exit={{ scale: 0 }}
                    >
                      <Send size={18} />
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.button>
            </div>
          </form>

          {/* Loading Indicator */}
          <AnimatePresence>
            {sendMessageMutation.isPending && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="px-4 pb-2"
              >
                <div className="text-xs text-gray-500 dark:text-gray-400 flex items-center space-x-2">
                  <motion.div
                    animate={{ opacity: [1, 0.5, 1] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="flex space-x-1"
                  >
                    <div className="w-1 h-1 bg-primary-500 rounded-full" />
                    <div className="w-1 h-1 bg-primary-500 rounded-full animation-delay-100" />
                    <div className="w-1 h-1 bg-primary-500 rounded-full animation-delay-200" />
                  </motion.div>
                  <span>WhoKnows is thinking...</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Keyboard Shortcuts */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-center"
        >
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Press{' '}
            <kbd className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs font-mono">
              Enter
            </kbd>{' '}
            to send,{' '}
            <kbd className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs font-mono">
              Shift + Enter
            </kbd>{' '}
            for new line
          </p>
        </motion.div>
      </div>
    </motion.div>
  )
}