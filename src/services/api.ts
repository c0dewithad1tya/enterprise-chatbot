import type { ChatResponse, ApiError } from '@/types'

const API_BASE_URL = 'http://localhost:5000'

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        const error: ApiError = {
          message: errorData.message || `HTTP ${response.status}: ${response.statusText}`,
          status: response.status,
          code: errorData.code,
        }
        throw error
      }

      return await response.json()
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        // Network error
        const networkError: ApiError = {
          message: 'Unable to connect to the server. Please ensure the backend is running.',
          status: 0,
          code: 'NETWORK_ERROR',
        }
        throw networkError
      }
      
      // Re-throw API errors
      throw error
    }
  }

  async sendMessage(query: string): Promise<ChatResponse> {
    return this.request<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ query }),
    })
  }

  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/api/health')
  }
}

export const apiService = new ApiService()

// React Query keys
export const queryKeys = {
  chat: (query: string) => ['chat', query] as const,
  health: () => ['health'] as const,
} as const