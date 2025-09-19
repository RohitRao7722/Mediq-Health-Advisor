import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Helper function to generate chat title from message content
const generateChatTitle = (message: string): string => {
  // Remove extra whitespace and limit length
  const cleanMessage = message.trim().replace(/\s+/g, ' ')
  
  // Health-related keywords for better categorization
  const healthKeywords = {
    'chest pain|heart attack|cardiac': 'Chest Pain Inquiry',
    'diabetes|blood sugar|insulin': 'Diabetes Questions',
    'headache|migraine': 'Headache Concerns',
    'fever|temperature': 'Fever Symptoms',
    'cough|cold|flu': 'Cold & Flu',
    'stomach|nausea|vomit': 'Digestive Issues',
    'anxiety|stress|mental': 'Mental Health',
    'pregnancy|pregnant': 'Pregnancy Questions',
    'medication|drug|pill': 'Medication Inquiry',
    'vaccine|vaccination': 'Vaccination Info',
    'diet|nutrition|food': 'Nutrition & Diet',
    'exercise|fitness|workout': 'Fitness & Exercise',
    'sleep|insomnia': 'Sleep Issues',
    'skin|rash|acne': 'Skin Conditions',
    'back pain|spine': 'Back Pain',
    'allergy|allergic': 'Allergy Questions'
  }
  
  // Check for health keywords
  for (const [keywords, title] of Object.entries(healthKeywords)) {
    const regex = new RegExp(keywords, 'i')
    if (regex.test(cleanMessage)) {
      return title
    }
  }
  
  // If no specific health keyword found, create title from first few words
  const words = cleanMessage.split(' ')
  if (words.length <= 3) {
    return cleanMessage.length > 30 ? cleanMessage.substring(0, 30) + '...' : cleanMessage
  }
  
  // Take first 3-4 meaningful words
  const meaningfulWords = words.filter(word => 
    word.length > 2 && 
    !['the', 'and', 'but', 'for', 'are', 'can', 'you', 'how', 'what', 'when', 'where', 'why'].includes(word.toLowerCase())
  )
  
  const titleWords = meaningfulWords.slice(0, 3).join(' ')
  return titleWords.length > 30 ? titleWords.substring(0, 30) + '...' : titleWords || 'Health Question'
}

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  sources?: Source[]
  isStreaming?: boolean
  error?: string
  rating?: 'positive' | 'negative' | null
  feedback?: string
}

export interface Source {
  id: string
  title: string
  url?: string
  content: string
  relevanceScore: number
  metadata: Record<string, any>
}

export interface ChatSession {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
  updatedAt: Date
}

export interface Settings {
  model: string
  temperature: number
  maxTokens: number
  showSources: boolean
  enableStreaming: boolean
  theme: 'light' | 'dark' | 'auto'
  fontSize: 'small' | 'medium' | 'large'
  voiceEnabled: boolean
}

interface ChatState {
  // Current session
  currentSessionId: string | null
  sessions: ChatSession[]
  messages: Message[]
  
  // UI state
  isSidebarOpen: boolean
  isSettingsOpen: boolean
  isTyping: boolean
  isConnected: boolean
  
  // API Key management
  userApiKey: string | null
  isApiKeySet: boolean
  
  // Settings
  settings: Settings
  
  // Actions
  createNewSession: () => void
  setCurrentSession: (sessionId: string) => void
  addMessage: (message: Omit<Message, 'id' | 'timestamp'> & { id?: string }) => void
  updateMessage: (messageId: string, updates: Partial<Message>) => void
  deleteMessage: (messageId: string) => void
  clearSession: () => void
  deleteSession: (sessionId: string) => void
  renameSession: (sessionId: string, newTitle: string) => void
  deleteAllSessions: () => void
  
  // UI actions
  toggleSidebar: () => void
  toggleSettings: () => void
  setTyping: (isTyping: boolean) => void
  setConnected: (isConnected: boolean) => void
  
  // API Key actions
  setApiKey: (apiKey: string | null) => void
  clearApiKey: () => void
  
  // Settings actions
  updateSettings: (settings: Partial<Settings>) => void
  resetSettings: () => void
  
  // Message actions
  rateMessage: (messageId: string, rating: 'positive' | 'negative') => void
  addFeedback: (messageId: string, feedback: string) => void
  
  // Debug actions
  debugStorage: () => void
}

const defaultSettings: Settings = {
  model: 'llama-3.1-8b-instant',
  temperature: 0.3,
  maxTokens: 1000,
  showSources: true,
  enableStreaming: true,
  theme: 'auto',
  fontSize: 'medium',
  voiceEnabled: false,
}

export const useChatStore = create<ChatState>()(persist(
  (set, get) => ({
    // Initial state
    currentSessionId: null,
    sessions: [],
    messages: [],
    isSidebarOpen: false,
    isSettingsOpen: false,
    isTyping: false,
    isConnected: false,
    userApiKey: null,
    isApiKeySet: false,
    settings: defaultSettings,
      
      // Session management
      createNewSession: () => {
        const newSession: ChatSession = {
          id: `session_${Date.now()}`,
          title: 'New Chat',
          messages: [],
          createdAt: new Date(),
          updatedAt: new Date(),
        }
        
        set((state) => ({
          sessions: [newSession, ...state.sessions],
          currentSessionId: newSession.id,
          messages: [],
        }))
      },
      
      setCurrentSession: (sessionId: string) => {
        const session = get().sessions.find(s => s.id === sessionId)
        if (session) {
          set({
            currentSessionId: sessionId,
            messages: session.messages,
          })
        }
      },
      
      // Message management
      addMessage: (messageData) => {
        const message: Message = {
          ...messageData,
          id: messageData.id || `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date(),
        }
        
        set((state) => {
          const newMessages = [...state.messages, message]
          
          // Auto-generate title for new chats based on first user message
          const shouldUpdateTitle = message.role === 'user' && 
                                   state.messages.length === 0 && 
                                   message.content.trim().length > 0
          
          const updatedSessions = state.sessions.map(session => {
            if (session.id === state.currentSessionId) {
              const updatedSession = { 
                ...session, 
                messages: newMessages, 
                updatedAt: new Date() 
              }
              
              // Update title if this is the first user message
              if (shouldUpdateTitle) {
                updatedSession.title = generateChatTitle(message.content)
              }
              
              return updatedSession
            }
            return session
          })
          
          return {
            messages: newMessages,
            sessions: updatedSessions,
          }
        })
      },
      
      updateMessage: (messageId, updates) => {
        set((state) => {
          const newMessages = state.messages.map(msg =>
            msg.id === messageId ? { ...msg, ...updates } : msg
          )
          
          const updatedSessions = state.sessions.map(session =>
            session.id === state.currentSessionId
              ? { ...session, messages: newMessages, updatedAt: new Date() }
              : session
          )
          
          return {
            messages: newMessages,
            sessions: updatedSessions,
          }
        })
      },
      
      deleteMessage: (messageId) => {
        set((state) => {
          const newMessages = state.messages.filter(msg => msg.id !== messageId)
          
          const updatedSessions = state.sessions.map(session =>
            session.id === state.currentSessionId
              ? { ...session, messages: newMessages, updatedAt: new Date() }
              : session
          )
          
          return {
            messages: newMessages,
            sessions: updatedSessions,
          }
        })
      },
      
      clearSession: () => {
        set((state) => {
          const updatedSessions = state.sessions.map(session =>
            session.id === state.currentSessionId
              ? { ...session, messages: [], updatedAt: new Date() }
              : session
          )
          
          return {
            messages: [],
            sessions: updatedSessions,
          }
        })
      },
      
      deleteSession: (sessionId) => {
        console.log('🗑️ Store deleteSession called with:', sessionId)
        
        const currentState = get()
        console.log('📊 Current sessions in store:', currentState.sessions.map(s => ({ id: s.id, title: s.title })))
        
        if (!currentState.sessions.find(s => s.id === sessionId)) {
          console.warn('⚠️ Session not found:', sessionId)
          return
        }
        
        const newSessions = currentState.sessions.filter(s => s.id !== sessionId)
        const isCurrentSession = currentState.currentSessionId === sessionId
        
        console.log('🔄 New sessions after filter:', newSessions.map(s => ({ id: s.id, title: s.title })))
        console.log('🎯 Is current session being deleted:', isCurrentSession)
        
        // Multiple update strategies for reliability
        const newState = {
          sessions: newSessions,
          currentSessionId: isCurrentSession ? null : currentState.currentSessionId,
          messages: isCurrentSession ? [] : currentState.messages,
        }
        
        // Strategy 1: Direct state update
        set(newState)
        
        // Strategy 2: Force localStorage update
        try {
          const storageKey = 'health-chatbot-storage'
          const stored = localStorage.getItem(storageKey)
          if (stored) {
            const parsedData = JSON.parse(stored)
            if (parsedData.state) {
              parsedData.state.sessions = newSessions
              parsedData.state.currentSessionId = newState.currentSessionId
              localStorage.setItem(storageKey, JSON.stringify(parsedData))
              console.log('💾 localStorage updated directly')
            }
          }
        } catch (error) {
          console.error('❌ localStorage update failed:', error)
        }
        
        // Strategy 3: Verification and retry
        setTimeout(() => {
          const verifyState = get()
          console.log('✅ Verification - Sessions after deletion:', verifyState.sessions.length)
          
          if (verifyState.sessions.find(s => s.id === sessionId)) {
            console.warn('⚠️ Session still exists after deletion, forcing another update')
            set({
              sessions: verifyState.sessions.filter(s => s.id !== sessionId),
              currentSessionId: verifyState.currentSessionId === sessionId ? null : verifyState.currentSessionId,
              messages: verifyState.currentSessionId === sessionId ? [] : verifyState.messages,
            })
          } else {
            console.log('✅ Session successfully deleted')
          }
        }, 100)
      },
      
      renameSession: (sessionId: string, newTitle: string) => {
        set((state) => {
          const updatedSessions = state.sessions.map(session =>
            session.id === sessionId
              ? { ...session, title: newTitle.trim() || 'Untitled Chat', updatedAt: new Date() }
              : session
          )
          
          return {
            sessions: updatedSessions,
          }
        })
      },
      
      deleteAllSessions: () => {
        console.log('🗑️🗑️ Store deleteAllSessions called')
        const currentState = get()
        const sessionCount = currentState.sessions.length
        console.log('📊 Sessions before clear:', sessionCount, currentState.sessions.map(s => ({ id: s.id, title: s.title })))
        
        if (sessionCount === 0) {
          console.log('🚀 No sessions to delete')
          return
        }
        
        const clearState = {
          sessions: [],
          currentSessionId: null,
          messages: [],
        }
        
        // Strategy 1: Direct state clear
        set(clearState)
        console.log('🔄 State cleared directly')
        
        // Strategy 2: Aggressive localStorage clearing
        try {
          const possibleKeys = ['health-chatbot-storage', 'chat-store', 'chatStore']
          let clearedAny = false
          
          possibleKeys.forEach(key => {
            const stored = localStorage.getItem(key)
            if (stored) {
              console.log(`🔍 Found data in localStorage key: ${key}`)
              try {
                const parsedData = JSON.parse(stored)
                if (parsedData.state) {
                  parsedData.state.sessions = []
                  parsedData.state.currentSessionId = null
                  parsedData.state.messages = []
                  localStorage.setItem(key, JSON.stringify(parsedData))
                  console.log(`💾 Cleared localStorage key: ${key}`)
                  clearedAny = true
                }
              } catch (parseError) {
                console.error(`❌ Error parsing localStorage key ${key}:`, parseError)
                localStorage.removeItem(key)
                console.log(`🗑️ Removed corrupted localStorage key: ${key}`)
              }
            }
          })
          
          if (!clearedAny) {
            console.log('🔍 No localStorage data found to clear')
          }
        } catch (error) {
          console.error('❌ Error during localStorage clearing:', error)
        }
        
        // Strategy 3: Multiple verification attempts
        const verifyAndRetry = (attempt = 1, maxAttempts = 3) => {
          setTimeout(() => {
            const verifyState = get()
            console.log(`✅ Verification attempt ${attempt} - Sessions remaining:`, verifyState.sessions.length)
            
            if (verifyState.sessions.length > 0) {
              console.warn(`⚠️ Attempt ${attempt}: ${verifyState.sessions.length} sessions still exist after clear`)
              
              if (attempt < maxAttempts) {
                // Force another clear
                set(clearState)
                verifyAndRetry(attempt + 1, maxAttempts)
              } else {
                console.error('❌ CRITICAL: Failed to clear sessions after multiple attempts')
                // Last resort: page refresh
                console.log('🔄 Forcing page refresh as last resort')
                setTimeout(() => window.location.reload(), 1000)
              }
            } else {
              console.log(`✅ SUCCESS: All sessions cleared on attempt ${attempt}`)
            }
          }, 100 * attempt)
        }
        
        verifyAndRetry()
      },
      
      // UI actions
      toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
      toggleSettings: () => set((state) => ({ isSettingsOpen: !state.isSettingsOpen })),
      setTyping: (isTyping) => set({ isTyping }),
      setConnected: (isConnected) => set({ isConnected }),
      
      // API Key actions
      setApiKey: (apiKey) => {
        set({
          userApiKey: apiKey,
          isApiKeySet: true,
        })
      },
      
      clearApiKey: () => {
        set({
          userApiKey: null,
          isApiKeySet: false,
        })
      },
      
      // Settings actions
      updateSettings: (newSettings) => {
        set((state) => ({
          settings: { ...state.settings, ...newSettings },
        }))
      },
      
      resetSettings: () => {
        set({ settings: defaultSettings })
      },
      
      // Message actions
      rateMessage: (messageId, rating) => {
        get().updateMessage(messageId, { rating })
      },
      
      addFeedback: (messageId, feedback) => {
        get().updateMessage(messageId, { feedback })
      },
      
      // Debug function to inspect localStorage
      debugStorage: () => {
        console.log('🔍=== STORAGE DEBUG ===')
        const currentState = get()
        console.log('📊 Current Zustand state:', {
          sessionCount: currentState.sessions.length,
          sessions: currentState.sessions.map(s => ({ id: s.id, title: s.title })),
          currentSessionId: currentState.currentSessionId
        })
        
        // Check localStorage
        const storageKey = 'health-chatbot-storage'
        const stored = localStorage.getItem(storageKey)
        if (stored) {
          try {
            const parsedData = JSON.parse(stored)
            console.log('💾 localStorage data:', {
              sessionCount: parsedData.state?.sessions?.length || 0,
              sessions: parsedData.state?.sessions?.map((s: any) => ({ id: s.id, title: s.title })) || [],
              currentSessionId: parsedData.state?.currentSessionId
            })
          } catch (error) {
            console.error('❌ Error parsing localStorage:', error)
          }
        } else {
          console.log('🔍 No localStorage data found')
        }
        console.log('🔍=== END DEBUG ===')
      },
    }),
    {
      name: 'health-chatbot-storage',
      partialize: (state) => ({
        sessions: state.sessions,
        currentSessionId: state.currentSessionId,
        settings: state.settings,
        userApiKey: state.userApiKey,
        isApiKeySet: state.isApiKeySet,
      }),
      // Force immediate persistence
      onRehydrateStorage: () => (state) => {
        console.log('Store rehydrated:', state ? {
          sessionCount: state.sessions?.length || 0,
          currentSession: state.currentSessionId
        } : 'null')
      },
    }
  )
)
