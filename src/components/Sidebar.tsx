import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Plus, 
  MessageSquare, 
  Moon, 
  Sun, 
  Monitor, 
  ChevronLeft, 
  ChevronRight,
  Settings,
  User,
  Trash2
} from 'lucide-react'
import { useChatStore } from '@/store/chat'
import { useSettingsStore } from '@/store/settings'
import { formatTimestamp, cn } from '@/lib/utils'

export function Sidebar() {
  const { 
    currentChat, 
    chatHistory, 
    createNewChat, 
    loadChat, 
    deleteChat 
  } = useChatStore()
  
  const { 
    sidebarCollapsed, 
    toggleSidebar, 
    theme, 
    setTheme 
  } = useSettingsStore()

  const handleChatClick = (chatId: string) => {
    loadChat(chatId)
  }

  const handleDeleteChat = (e: React.MouseEvent, chatId: string) => {
    e.stopPropagation()
    if (window.confirm('Are you sure you want to delete this chat?')) {
      deleteChat(chatId)
    }
  }

  const themeOptions = [
    { value: 'light', icon: Sun, label: 'Light' },
    { value: 'dark', icon: Moon, label: 'Dark' },
    { value: 'system', icon: Monitor, label: 'System' },
  ] as const

  return (
    <motion.div
      initial={{ x: -300 }}
      animate={{ x: 0 }}
      className={cn(
        'h-full glass glass-border border-r flex flex-col',
        'transition-all duration-300 ease-in-out'
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <AnimatePresence mode="wait">
          {!sidebarCollapsed ? (
            <motion.div
              key="expanded"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center justify-between"
            >
              <div className="flex items-center space-x-3">
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className="w-8 h-8 rounded-lg bg-gray-900 dark:bg-gray-100 flex items-center justify-center text-white dark:text-gray-900 font-bold text-sm shadow-sm"
                >
                  W
                </motion.div>
                <h2 className="text-lg font-semibold gradient-text">WhoKnows?</h2>
              </div>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={toggleSidebar}
                className="p-1.5 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <ChevronLeft size={16} />
              </motion.button>
            </motion.div>
          ) : (
            <motion.div
              key="collapsed"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center space-y-3"
            >
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="w-8 h-8 rounded-lg bg-gray-900 dark:bg-gray-100 flex items-center justify-center text-white dark:text-gray-900 font-bold text-sm shadow-sm"
              >
                W
              </motion.div>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={toggleSidebar}
                className="p-1.5 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <ChevronRight size={16} />
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* New Chat Button */}
      <div className="p-4">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={createNewChat}
          className={cn(
            'w-full flex items-center justify-center space-x-2 px-4 py-3',
            'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900',
            'rounded-xl hover:bg-gray-800 dark:hover:bg-gray-200',
            'transition-all duration-200 shadow-sm hover:shadow-md',
            sidebarCollapsed && 'px-2'
          )}
        >
          <Plus size={18} />
          {!sidebarCollapsed && <span className="font-medium">New Chat</span>}
        </motion.button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-hidden">
        {!sidebarCollapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="px-4 pb-2"
          >
            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              Recent Chats
            </h3>
          </motion.div>
        )}

        <div className="px-2 space-y-1 overflow-y-auto scrollbar-thin max-h-[calc(100vh-300px)]">
          <AnimatePresence>
            {chatHistory.length === 0 ? (
              !sidebarCollapsed && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="p-4 text-center text-gray-500 dark:text-gray-400 text-sm"
                >
                  No recent chats
                </motion.div>
              )
            ) : (
              chatHistory.map((chat, index) => (
                <motion.div
                  key={chat.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -100 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => handleChatClick(chat.id)}
                  className={cn(
                    'group relative p-3 rounded-lg cursor-pointer transition-all duration-200',
                    'hover:bg-gray-100 dark:hover:bg-gray-800',
                    currentChat?.id === chat.id 
                      ? 'bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600' 
                      : 'hover:shadow-md'
                  )}
                >
                  {!sidebarCollapsed ? (
                    <>
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                            {chat.title}
                          </h4>
                          <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-1">
                            {chat.preview}
                          </p>
                          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                            {formatTimestamp(new Date(chat.timestamp))}
                          </p>
                        </div>
                        
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={(e) => handleDeleteChat(e, chat.id)}
                          className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition-all duration-200"
                        >
                          <Trash2 size={14} />
                        </motion.button>
                      </div>
                    </>
                  ) : (
                    <div className="flex justify-center">
                      <MessageSquare 
                        size={18} 
                        className={cn(
                          currentChat?.id === chat.id 
                            ? 'text-gray-900 dark:text-gray-100' 
                            : 'text-gray-600 dark:text-gray-400'
                        )}
                      />
                    </div>
                  )}
                </motion.div>
              ))
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-3">
        {!sidebarCollapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-3"
          >
            {/* Theme Selector */}
            <div>
              <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
                Theme
              </h4>
              <div className="flex space-x-1">
                {themeOptions.map(({ value, icon: Icon, label }) => (
                  <motion.button
                    key={value}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setTheme(value)}
                    className={cn(
                      'flex-1 flex items-center justify-center p-2 rounded-lg transition-all duration-200',
                      theme.mode === value
                        ? 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400'
                    )}
                    title={label}
                  >
                    <Icon size={16} />
                  </motion.button>
                ))}
              </div>
            </div>

            {/* User Info */}
            <div className="flex items-center space-x-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
              <div className="w-8 h-8 bg-gray-700 dark:bg-gray-300 rounded-full flex items-center justify-center text-white dark:text-gray-900 font-bold text-sm">
                U
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  Enterprise User
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  user@company.com
                </div>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <Settings size={16} />
              </motion.button>
            </div>
          </motion.div>
        )}

        {sidebarCollapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center space-y-3"
          >
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setTheme(theme.mode === 'dark' ? 'light' : 'dark')}
              className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              {theme.mode === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="w-8 h-8 bg-gray-700 dark:bg-gray-300 rounded-full flex items-center justify-center text-white dark:text-gray-900 font-bold text-sm"
            >
              U
            </motion.button>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}