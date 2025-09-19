import React, { useEffect, useState } from 'react'
import { Box, CssBaseline, useMediaQuery, useTheme, CircularProgress, Typography } from '@mui/material'
import { useChatStore } from './store/chatStore'
import { apiService } from './services/api'
import ChatInterface from './components/ChatInterface'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import SettingsPanel from './components/SettingsPanel'
import ApiKeyDialog from './components/ApiKeyDialog'
import { toast } from 'react-hot-toast'

function App() {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  
  const {
    isSidebarOpen,
    isSettingsOpen,
    isConnected,
    setConnected,
    createNewSession,
    currentSessionId,
    settings,
    isApiKeySet,
    setApiKey,
  } = useChatStore()
  
  const handleApiKeySet = (apiKey: string | null) => {
    setApiKey(apiKey)
  }

  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Initialize app
  useEffect(() => {
    const initializeApp = async () => {
      try {
        setIsLoading(true)
        setError(null)

        // Check API health
        const health = await apiService.healthCheck()
        if (health.status === 'healthy') {
          setConnected(true)
          toast.success('Connected to health chatbot service')
        } else {
          throw new Error('Service is not healthy')
        }

        // Get API info
        const info = await apiService.getApiInfo()
        console.log('API Info:', info)

        // Create initial session if none exists
        if (!currentSessionId) {
          createNewSession()
        }

      } catch (err: any) {
        console.error('Failed to initialize app:', err)
        setError(err.message || 'Failed to connect to the health chatbot service')
        setConnected(false)
        toast.error('Failed to connect to health chatbot service')
      } finally {
        setIsLoading(false)
      }
    }

    initializeApp()
  }, [createNewSession, currentSessionId, setConnected])

  // Handle connection status
  useEffect(() => {
    const checkConnection = async () => {
      try {
        await apiService.healthCheck()
        if (!isConnected) {
          setConnected(true)
        }
      } catch {
        if (isConnected) {
          setConnected(false)
          toast.error('Connection lost. Please check your internet connection.')
        }
      }
    }

    // Check connection every 30 seconds
    const interval = setInterval(checkConnection, 30000)
    return () => clearInterval(interval)
  }, [isConnected, setConnected])

  // Theme is now handled by CustomThemeProvider

  // Handle font size changes
  useEffect(() => {
    const root = document.documentElement
    root.style.fontSize = settings.fontSize === 'small' ? '14px' : 
                         settings.fontSize === 'large' ? '18px' : '16px'
  }, [settings.fontSize])

  if (isLoading) {
    return (
      <Box
        sx={{
          height: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
        }}
      >
        <CircularProgress sx={{ color: 'white', mb: 2 }} />
        <Typography variant="h6">Loading Health Chatbot...</Typography>
      </Box>
    )
  }

  if (error) {
    return (
      <Box
        sx={{
          height: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          textAlign: 'center',
          p: 3,
        }}
      >
        <h1>🏥 Health Chatbot</h1>
        <p style={{ marginBottom: '2rem', opacity: 0.9 }}>
          {error}
        </p>
        <button
          onClick={() => window.location.reload()}
          style={{
            padding: '12px 24px',
            background: 'rgba(255,255,255,0.2)',
            border: '1px solid rgba(255,255,255,0.3)',
            borderRadius: '8px',
            color: 'white',
            cursor: 'pointer',
            fontSize: '16px',
          }}
        >
          Retry Connection
        </button>
      </Box>
    )
  }

  return (
    <>
      {/* API Key Dialog */}
      <ApiKeyDialog 
        open={!isApiKeySet}
        onApiKeySet={handleApiKeySet}
      />
      
      <Box sx={{ 
        display: 'flex', 
        minHeight: '100vh',
        height: '100%',
        overflow: 'hidden'
      }}>
        <CssBaseline />
        
        {/* Header - positioned absolutely to not affect layout */}
        <Header />
        
        {/* Sidebar - Always open on desktop */}
        {!isMobile && (
          <Sidebar 
            open={true}
            onClose={() => {}} // No close action on desktop
          />
        )}
        
        {/* Mobile Sidebar Overlay */}
        {isMobile && isSidebarOpen && (
          <Box
            sx={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: 1300,
              background: 'rgba(0,0,0,0.5)',
            }}
            onClick={() => useChatStore.getState().toggleSidebar()}
          />
        )}
        
        {/* Main Content */}
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            minHeight: 0, // Important for flex child to shrink
            overflow: 'hidden',
          }}
        >
          <ChatInterface />
        </Box>
        
        {/* Settings Panel */}
        <SettingsPanel 
          open={isSettingsOpen}
          onClose={() => useChatStore.getState().toggleSettings()}
        />
      </Box>
    </>
  )
}

export default App
