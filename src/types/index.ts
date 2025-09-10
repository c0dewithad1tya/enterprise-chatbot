export interface Confidence {
  level: 'high' | 'medium' | 'low'
  score: number
  explanation?: string
}

export interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: Source[]
  confidence?: Confidence
  isLoading?: boolean
}

export interface Source {
  type: 'document' | 'url'
  title: string
  path?: string
  url?: string
}

export interface Chat {
  id: string
  title: string
  messages: Message[]
  timestamp: Date
  preview: string
}

export interface ChatResponse {
  message: string
  sources: Source[]
  confidence?: Confidence
}

export interface User {
  id: string
  name: string
  email: string
  avatar?: string
}

export interface Theme {
  mode: 'light' | 'dark' | 'system'
}

export interface AppSettings {
  theme: Theme
  sidebarCollapsed: boolean
  autoSave: boolean
  soundEnabled: boolean
}

export interface ChatState {
  currentChat: Chat | null
  chatHistory: Chat[]
  isLoading: boolean
  error: string | null
}

export interface ApiError {
  message: string
  status: number
  code?: string
}