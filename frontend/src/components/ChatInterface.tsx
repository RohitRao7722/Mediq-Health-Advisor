import React, { useRef, useEffect, useState } from 'react'
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Typography,
  Tooltip,
  useTheme,
} from '@mui/material'
import {
  Send as SendIcon,
  AttachFile as AttachIcon,
  Mic as MicIcon,
} from '@mui/icons-material'
import { useChatStore } from '../store/chatStore'
import { apiService } from '../services/api'
import MessageList from './MessageList'
import TypingIndicator from './TypingIndicator'
import ConnectionStatus from './ConnectionStatus'
import WelcomeContent from './WelcomeContent'
import { toast } from 'react-hot-toast'

const ChatInterface: React.FC = () => {
  const theme = useTheme()
  
  const {
    messages,
    isTyping,
    isConnected,
    addMessage,
    updateMessage,
    setTyping,
    currentSessionId,
    settings,
    userApiKey,
  } = useChatStore()

  const [inputValue, setInputValue] = useState('')
  const [isSending, setIsSending] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isSending || !isConnected) return

    const userMessage = inputValue.trim()
    setInputValue('')
    setIsSending(true)

    // Add user message
    addMessage({
      content: userMessage,
      role: 'user',
    })

    // Add assistant message placeholder
    const assistantMessageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    addMessage({
      id: assistantMessageId,
      content: '',
      role: 'assistant',
      isStreaming: true,
    })

    setTyping(true)

    try {
      const response = await apiService.sendMessage({
        message: userMessage,
        sessionId: currentSessionId || undefined,
        settings: {
          temperature: settings.temperature,
          maxTokens: settings.maxTokens,
          enableStreaming: settings.enableStreaming,
        },
      }, userApiKey)

      // Update assistant message with response
      updateMessage(assistantMessageId, {
        content: response.response,
        isStreaming: false,
        sources: response.sources || [],
      })

    } catch (error: any) {
      console.error('Failed to send message:', error)
      
      // Update assistant message with error
      updateMessage(assistantMessageId, {
        content: `I apologize, but I encountered an error: ${error.message}. Please try again or consult a healthcare professional for immediate medical concerns.`,
        isStreaming: false,
        error: error.message,
      })
      
      toast.error('Failed to send message. Please try again.')
    } finally {
      setTyping(false)
      setIsSending(false)
    }
  }

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSendMessage()
    }
  }

  // Voice recording temporarily disabled - feature under development
  const handleVoiceToggle = () => {
    toast('Voice recording feature coming soon!', { 
      icon: '🎤',
      duration: 2000
    })
  }

  const handleFileUpload = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.txt,.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.bmp,.webp'
    input.multiple = false
    
    input.onchange = async (event) => {
      const file = (event.target as HTMLInputElement).files?.[0]
      if (!file) return
      
      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast('File size must be less than 10MB', { icon: '⚠️' })
        return
      }
      
      try {
        setIsSending(true)
        
        // Add file message to chat
        const fileMessage = `📎 Uploaded file: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`
        addMessage({
          content: fileMessage,
          role: 'user',
        })
        
        // Process file based on type
        let fileContent = ''
        
        if (file.type.startsWith('text/') || file.name.endsWith('.txt')) {
          // Handle text files
          fileContent = await file.text()
        } else if (file.type.startsWith('image/')) {
          // Handle images - convert to base64
          const reader = new FileReader()
          fileContent = await new Promise((resolve) => {
            reader.onload = () => resolve(reader.result as string)
            reader.readAsDataURL(file)
          })
        } else {
          // For other file types, just show file info
          fileContent = `File uploaded: ${file.name} (${file.type})`
        }
        
        // Create analysis prompt
        let analysisPrompt = ''
        if (file.type.startsWith('text/') || file.name.endsWith('.txt')) {
          analysisPrompt = `Please analyze this document content and provide health-related insights if applicable:\n\n${fileContent}`
        } else if (file.type.startsWith('image/')) {
          analysisPrompt = `I've uploaded an image file (${file.name}). Please note that I cannot directly analyze images, but if you can describe what health-related information you're looking for, I can provide relevant guidance.`
        } else {
          analysisPrompt = `I've uploaded a file (${file.name}). Please note that I can currently process text files directly. For other file types, please describe what health information you're looking for and I'll provide relevant guidance.`
        }
        
        // Add assistant message placeholder
        const assistantMessageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        addMessage({
          id: assistantMessageId,
          content: '',
          role: 'assistant',
          isStreaming: true,
        })
        
        // Send to backend
        const response = await apiService.sendMessage({
          message: analysisPrompt,
          sessionId: currentSessionId || undefined,
          settings: {
            temperature: settings.temperature,
            maxTokens: settings.maxTokens,
            enableStreaming: false
          }
        }, userApiKey)
        
        // Update the assistant message with the response
        updateMessage(assistantMessageId, { 
          content: response.response,
          isStreaming: false,
          sources: response.sources
        })
        
        toast('File processed successfully!', { icon: '✅' })
        
      } catch (error) {
        console.error('File upload error:', error)
        toast('Error processing file. Please try again.', { icon: '❌' })
      } finally {
        setIsSending(false)
      }
    }
    
    input.click()
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        background: theme.palette.mode === 'dark' 
          ? 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)'
          : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: theme.palette.mode === 'dark'
            ? 'radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.2) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.05) 0%, transparent 50%)'
            : 'radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%)',
          pointerEvents: 'none',
        },
      }}
    >
      {/* Connection Status */}
      <ConnectionStatus />
      
      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          zIndex: 1,
          minHeight: 0, // Important for flex child to shrink
          pt: '80px', // Add top padding to account for fixed header
          scrollBehavior: 'smooth',
          '&::-webkit-scrollbar': {
            width: '6px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'transparent',
          },
          '&::-webkit-scrollbar-thumb': {
            background: theme.palette.mode === 'dark' 
              ? 'rgba(255,255,255,0.2)' 
              : 'rgba(0,0,0,0.2)',
            borderRadius: '3px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            background: theme.palette.mode === 'dark' 
              ? 'rgba(255,255,255,0.3)' 
              : 'rgba(0,0,0,0.3)',
          },
        }}
      >
        {/* Welcome Content - shown at top when no messages */}
        {messages.length === 0 && !isTyping && (
          <Box
            sx={{
              position: 'sticky',
              top: 0,
              zIndex: 2,
              background: theme.palette.mode === 'dark' 
                ? 'rgba(30, 30, 30, 0.95)' 
                : 'rgba(255,255,255,0.95)',
              backdropFilter: 'blur(20px)',
              borderBottom: theme.palette.mode === 'dark' 
                ? '1px solid rgba(255,255,255,0.1)' 
                : '1px solid rgba(0,0,0,0.05)',
            }}
          >
            <WelcomeContent />
          </Box>
        )}
        
        <MessageList />
        
        {/* Typing Indicator */}
        {isTyping && <TypingIndicator />}
        
        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Box
        sx={{
          p: { xs: 2, sm: 3 },
          background: theme.palette.mode === 'dark' 
            ? 'rgba(30, 30, 30, 0.98)' 
            : 'rgba(255,255,255,0.98)',
          backdropFilter: 'blur(20px)',
          borderTop: theme.palette.mode === 'dark' 
            ? '1px solid rgba(255,255,255,0.1)' 
            : '1px solid rgba(0,0,0,0.05)',
          position: 'relative',
          zIndex: 2,
          flexShrink: 0, // Prevent input area from shrinking
        }}
      >
        <Paper
          elevation={8}
          sx={{
            p: 2,
            display: 'flex',
            alignItems: 'flex-end',
            gap: 2,
            borderRadius: 4,
            background: theme.palette.background.paper,
            border: theme.palette.mode === 'dark' 
              ? '1px solid rgba(255,255,255,0.1)' 
              : '1px solid rgba(0,0,0,0.05)',
            boxShadow: theme.palette.mode === 'dark' 
              ? '0 8px 32px rgba(0,0,0,0.3)' 
              : '0 8px 32px rgba(0,0,0,0.1)',
            transition: 'all 0.3s ease',
            '&:hover': {
              boxShadow: theme.palette.mode === 'dark' 
                ? '0 12px 40px rgba(0,0,0,0.4)' 
                : '0 12px 40px rgba(0,0,0,0.15)',
            },
          }}
        >
          {/* File Upload Button */}
          <Tooltip title="Upload file (Text, PDF, Images - Max 10MB)" placement="top">
            <IconButton
              onClick={handleFileUpload}
              disabled={isSending}
              size="medium"
              aria-label="Upload file"
              sx={{ 
                color: isSending ? 'text.disabled' : 'text.secondary',
                background: 'rgba(0,0,0,0.02)',
                '&:hover': { 
                  color: 'primary.main',
                  background: 'rgba(25, 118, 210, 0.08)',
                  transform: 'scale(1.05)',
                },
                '&:disabled': {
                  color: 'text.disabled',
                  background: 'rgba(0,0,0,0.01)',
                },
                transition: 'all 0.2s ease',
              }}
            >
              <AttachIcon />
            </IconButton>
          </Tooltip>

          {/* Text Input */}
          <TextField
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              isConnected 
                ? "Ask me about health, symptoms, treatments, or wellness..." 
                : "Connecting to health chatbot service..."
            }
            disabled={isSending || !isConnected}
            multiline
            maxRows={4}
            variant="outlined"
            aria-label="Health question input"
            aria-describedby="chat-input-help"
            InputProps={{
              sx: {
                border: 'none',
                '& .MuiOutlinedInput-notchedOutline': {
                  border: 'none',
                },
                fontSize: '1rem',
                lineHeight: 1.5,
              },
            }}
            sx={{
              flex: 1,
              '& .MuiInputBase-root': {
                padding: 0,
              },
            }}
          />

          {/* Voice Recording Button */}
          <Tooltip title="Voice recording (Coming Soon)" placement="top">
            <IconButton
              onClick={handleVoiceToggle}
              disabled={isSending}
              size="medium"
              aria-label="Voice recording (Coming Soon)"
              sx={{ 
                color: 'text.secondary',
                background: 'rgba(0,0,0,0.02)',
                opacity: 0.6,
                '&:hover': { 
                  color: 'primary.main',
                  background: 'rgba(25, 118, 210, 0.08)',
                  transform: 'scale(1.05)',
                  opacity: 0.8,
                },
                transition: 'all 0.2s ease',
              }}
            >
              <MicIcon />
            </IconButton>
          </Tooltip>

          {/* Send Button */}
          <IconButton
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isSending || !isConnected}
            size="medium"
            aria-label="Send message"
            sx={{
              background: inputValue.trim() && isConnected 
                ? 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)' 
                : 'rgba(0,0,0,0.05)',
              color: inputValue.trim() && isConnected ? 'white' : 'text.disabled',
              minWidth: '48px',
              minHeight: '48px',
              '&:hover': {
                background: inputValue.trim() && isConnected 
                  ? 'linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)' 
                  : 'rgba(0,0,0,0.08)',
                transform: inputValue.trim() && isConnected ? 'scale(1.05)' : 'none',
              },
              '&:disabled': {
                background: 'rgba(0,0,0,0.03)',
                color: 'text.disabled',
              },
              transition: 'all 0.2s ease',
            }}
          >
            <SendIcon />
          </IconButton>
        </Paper>

        {/* Input Footer */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mt: 1,
            px: 1,
          }}
        >
          <Typography variant="caption" color="text.secondary">
            {isConnected ? 'Press Enter to send, Shift+Enter for new line' : 'Connecting...'}
          </Typography>
          
          {isSending && (
            <Typography variant="caption" color="primary.main">
              Sending...
            </Typography>
          )}
        </Box>
      </Box>
    </Box>
  )
}

export default ChatInterface
