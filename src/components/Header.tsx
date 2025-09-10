import { motion } from 'framer-motion'
import { Menu, Trash2, MoreVertical } from 'lucide-react'
import { useChatStore } from '@/store/chat'
import { useSettingsStore } from '@/store/settings'
import { cn } from '@/lib/utils'

export function Header() {
  const { currentChat, deleteChat, createNewChat } = useChatStore()
  const { sidebarCollapsed, toggleSidebar } = useSettingsStore()

  const handleDeleteChat = () => {
    if (currentChat && window.confirm('Are you sure you want to delete this chat?')) {
      deleteChat(currentChat.id)
      createNewChat()
    }
  }

  return (
    <motion.header
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="glass glass-border border-b px-6 py-4 flex items-center justify-between"
    >
      {/* Left side */}
      <div className="flex items-center space-x-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={toggleSidebar}
          className={cn(
            'p-2 rounded-lg transition-colors',
            'hover:bg-gray-100 dark:hover:bg-gray-800',
            sidebarCollapsed && 'hidden'
          )}
          aria-label="Toggle sidebar"
        >
          <Menu size={20} />
        </motion.button>

        <div className="flex items-center space-x-3">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm shadow-lg"
          >
            W
          </motion.div>
          
          <div>
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
              {currentChat?.title || 'WhoKnows?'}
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Enterprise Knowledge Assistant
            </p>
          </div>
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center space-x-2">
        {currentChat && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleDeleteChat}
            className="p-2 text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            title="Delete chat"
          >
            <Trash2 size={18} />
          </motion.button>
        )}

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          title="More options"
        >
          <MoreVertical size={18} />
        </motion.button>
      </div>
    </motion.header>
  )
}