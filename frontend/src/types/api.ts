export interface ChatRequest {
  message: string
  sessionId?: string
  settings?: {
    temperature?: number
    maxTokens?: number
    enableStreaming?: boolean
  }
}

export interface ChatResponse {
  response: string
  timestamp: string
  sources: SourceData[]
  topScore: number
  sessionId?: string
  metadata?: {
    model_used: string
    response_length: number
    sources_used: number
    processing_time: number
  }
}

export interface StreamingResponse {
  type: 'content' | 'sources' | 'done' | 'error'
  data: any
}

export interface SourceData {
  id: string
  title: string
  content: string
  relevanceScore: number
  metadata: {
    source: string
    chunk_index: number
    total_chunks: number
    chunk_size: number
    file_type?: string
  }
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy'
  timestamp: string
  vectors?: number
  error?: string
}

export interface ApiInfoResponse {
  model: string
  vectors: number
  embedding_model: string
  timestamp: string
}

export interface FeedbackRequest {
  messageId: string
  rating: 'positive' | 'negative'
  feedback?: string
}

export interface ErrorResponse {
  error: string
  message?: string
  code?: string
}
