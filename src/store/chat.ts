import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Chat, Message, ChatState } from '@/types'
import { generateId } from '@/lib/utils'

interface ChatStore extends ChatState {
  // Actions
  setCurrentChat: (chat: Chat | null) => void
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
  updateMessage: (messageId: string, updates: Partial<Message>) => void
  deleteMessage: (messageId: string) => void
  createNewChat: () => void
  deleteChat: (chatId: string) => void
  loadChat: (chatId: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      // Initial state
      currentChat: null,
      chatHistory: [],
      isLoading: false,
      error: null,

      // Actions
      setCurrentChat: (chat) => set({ currentChat: chat }),

      addMessage: (messageData) => {
        const message: Message = {
          ...messageData,
          id: generateId(),
          timestamp: new Date(),
        }

        set((state) => {
          let updatedChat = state.currentChat
          
          if (!updatedChat) {
            // Create new chat if none exists
            const chatTitle = message.content.length > 50 
              ? message.content.substring(0, 47) + '...'
              : message.content
              
            updatedChat = {
              id: generateId(),
              title: chatTitle,
              messages: [message],
              timestamp: new Date(),
              preview: message.content.substring(0, 100),
            }
          } else {
            // Add message to existing chat
            updatedChat = {
              ...updatedChat,
              messages: [...updatedChat.messages, message],
              timestamp: new Date(),
            }
          }

          // Update chat history
          const existingChatIndex = state.chatHistory.findIndex(
            (chat) => chat.id === updatedChat!.id
          )
          
          let updatedHistory = [...state.chatHistory]
          if (existingChatIndex !== -1) {
            updatedHistory[existingChatIndex] = updatedChat
          } else {
            updatedHistory.unshift(updatedChat)
          }

          // Keep only last 50 chats
          updatedHistory = updatedHistory.slice(0, 50)

          return {
            currentChat: updatedChat,
            chatHistory: updatedHistory,
          }
        })
      },

      updateMessage: (messageId, updates) => {
        set((state) => {
          if (!state.currentChat) return state

          const updatedMessages = state.currentChat.messages.map((msg) =>
            msg.id === messageId ? { ...msg, ...updates } : msg
          )

          const updatedChat = {
            ...state.currentChat,
            messages: updatedMessages,
          }

          const updatedHistory = state.chatHistory.map((chat) =>
            chat.id === updatedChat.id ? updatedChat : chat
          )

          return {
            currentChat: updatedChat,
            chatHistory: updatedHistory,
          }
        })
      },

      deleteMessage: (messageId) => {
        set((state) => {
          if (!state.currentChat) return state

          const updatedMessages = state.currentChat.messages.filter(
            (msg) => msg.id !== messageId
          )

          const updatedChat = {
            ...state.currentChat,
            messages: updatedMessages,
          }

          const updatedHistory = state.chatHistory.map((chat) =>
            chat.id === updatedChat.id ? updatedChat : chat
          )

          return {
            currentChat: updatedChat,
            chatHistory: updatedHistory,
          }
        })
      },

      createNewChat: () => {
        set({ currentChat: null, error: null })
      },

      deleteChat: (chatId) => {
        set((state) => {
          const updatedHistory = state.chatHistory.filter(
            (chat) => chat.id !== chatId
          )
          
          const currentChatDeleted = state.currentChat?.id === chatId
          
          return {
            chatHistory: updatedHistory,
            currentChat: currentChatDeleted ? null : state.currentChat,
          }
        })
      },

      loadChat: (chatId) => {
        const chat = get().chatHistory.find((c) => c.id === chatId)
        if (chat) {
          set({ currentChat: chat, error: null })
        }
      },

      setLoading: (loading) => set({ isLoading: loading }),
      
      setError: (error) => set({ error }),
      
      clearError: () => set({ error: null }),
    }),
    {
      name: 'whoknows-chat-storage',
      partialize: (state) => ({
        chatHistory: state.chatHistory,
      }),
    }
  )
)