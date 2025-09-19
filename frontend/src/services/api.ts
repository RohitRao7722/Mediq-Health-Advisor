import axios, { AxiosInstance, AxiosResponse } from 'axios'
import { 
  ChatRequest, 
  ChatResponse, 
  HealthCheckResponse, 
  ApiInfoResponse, 
  FeedbackRequest,
  ErrorResponse 
} from '../types/api'

class ApiService {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('API Request Error:', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.api.interceptors.response.use(
      (response) => {
        console.log(`API Response: ${response.status} ${response.config.url}`)
        return response
      },
      (error) => {
        console.error('API Response Error:', error)
        return Promise.reject(error)
      }
    )
  }

  // Health check
  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const response: AxiosResponse<HealthCheckResponse> = await this.api.get('/health')
      return response.data
    } catch (error) {
      console.error('Health check failed:', error)
      throw new Error('Unable to connect to the health chatbot service')
    }
  }

  // Get API info
  async getApiInfo(): Promise<ApiInfoResponse> {
    try {
      const response: AxiosResponse<ApiInfoResponse> = await this.api.get('/info')
      return response.data
    } catch (error) {
      console.error('Failed to get API info:', error)
      throw new Error('Unable to get system information')
    }
  }

  // Send chat message
  async sendMessage(request: ChatRequest, userApiKey?: string | null): Promise<ChatResponse> {
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }
      
      // Add user API key if provided
      if (userApiKey) {
        headers['X-User-API-Key'] = userApiKey
      }
      
      const response: AxiosResponse<ChatResponse> = await this.api.post('/chat', request, {
        headers
      })
      return response.data
    } catch (error: any) {
      console.error('Chat request failed:', error)
      
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error)
      } else if (error.code === 'ECONNABORTED') {
        throw new Error('Request timeout. Please try again.')
      } else if (error.code === 'NETWORK_ERROR') {
        throw new Error('Network error. Please check your connection.')
      } else {
        throw new Error('Failed to send message. Please try again.')
      }
    }
  }
  
  // Validate API key
  async validateApiKey(apiKey: string): Promise<boolean> {
    try {
      const response = await this.api.post('/validate-key', { apiKey })
      return response.status === 200
    } catch (error) {
      console.error('API key validation failed:', error)
      return false
    }
  }

  // Send feedback
  async sendFeedback(feedback: FeedbackRequest): Promise<void> {
    try {
      await this.api.post('/feedback', feedback)
    } catch (error) {
      console.error('Failed to send feedback:', error)
      // Don't throw error for feedback failures
    }
  }

  // Stream chat message (for future implementation)
  async *streamMessage(request: ChatRequest): AsyncGenerator<ChatResponse, void, unknown> {
    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body reader available')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              yield data
            } catch (e) {
              console.warn('Failed to parse streaming data:', e)
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming request failed:', error)
      throw error
    }
  }

  // Check if streaming is supported
  async supportsStreaming(): Promise<boolean> {
    try {
      const response = await fetch('/api/chat/stream', {
        method: 'HEAD',
      })
      return response.ok
    } catch {
      return false
    }
  }
}

export const apiService = new ApiService()
export default apiService
