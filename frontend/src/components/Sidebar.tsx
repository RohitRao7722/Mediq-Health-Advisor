import React from 'react'
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Box,
  IconButton,
  Divider,
  Chip,
} from '@mui/material'
import {
  Chat as ChatIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  History as HistoryIcon,
} from '@mui/icons-material'
import { useChatStore } from '../store/chatStore'
import { format } from 'date-fns'

interface SidebarProps {
  open: boolean
  onClose: () => void
}

const Sidebar: React.FC<SidebarProps> = ({ open }) => {
  const {
    sessions,
    currentSessionId,
    setCurrentSession,
    createNewSession,
    deleteSession,
    clearSession,
    deleteAllSessions,
  } = useChatStore()

  const handleNewChat = () => {
    createNewSession()
    // Don't close sidebar on desktop
  }

  const handleSessionSelect = (sessionId: string) => {
    setCurrentSession(sessionId)
    // Don't close sidebar on desktop
  }

  const handleDeleteSession = (sessionId: string, event: React.MouseEvent) => {
    event.stopPropagation()
    console.log('🗑️ SIDEBAR: Individual delete requested for:', sessionId)
    console.log('📊 SIDEBAR: Available sessions before delete:', sessions.map(s => ({ id: s.id, title: s.title })))
    
    const sessionToDelete = sessions.find(s => s.id === sessionId)
    if (!sessionToDelete) {
      console.error('❌ SIDEBAR: Session not found:', sessionId)
      return
    }
    
    const confirmMessage = `Delete "${sessionToDelete.title}"? This action cannot be undone.`
    
    if (window.confirm(confirmMessage)) {
      console.log('🚀 SIDEBAR: User confirmed deletion')
      
      try {
        deleteSession(sessionId)
        console.log('✅ SIDEBAR: Delete function called')
        
        // Verification after a short delay
        setTimeout(() => {
          const currentSessions = useChatStore.getState().sessions
          const stillExists = currentSessions.find(s => s.id === sessionId)
          
          if (stillExists) {
            console.error('❌ SIDEBAR: Session still exists after deletion attempt!')
            console.log('🔄 SIDEBAR: Current sessions:', currentSessions.map(s => ({ id: s.id, title: s.title })))
          } else {
            console.log('✅ SIDEBAR: Session successfully deleted')
          }
        }, 200)
        
      } catch (error) {
        console.error('❌ SIDEBAR: Error deleting session:', error)
      }
    } else {
      console.log('❌ SIDEBAR: Delete cancelled by user')
    }
  }
  
  const handleDeleteAllChats = () => {
    if (sessions.length === 0) {
      console.log('🚀 No sessions to delete')
      return
    }
    
    const confirmMessage = `Are you sure you want to delete ALL ${sessions.length} chat${sessions.length > 1 ? 's' : ''}? This action cannot be undone.`
    
    if (window.confirm(confirmMessage)) {
      console.log('🗑️🗑️ SIDEBAR: Starting bulk delete process')
      console.log('📊 SIDEBAR: Sessions before delete:', sessions.length, sessions.map(s => ({ id: s.id, title: s.title })))
      
      try {
        // Use the enhanced bulk delete function
        deleteAllSessions()
        console.log('🚀 SIDEBAR: Bulk delete initiated')
        
      } catch (error) {
        console.error('❌ SIDEBAR: Error during bulk delete:', error)
        
        // Emergency fallback: individual deletion
        console.log('🆘 SIDEBAR: Attempting individual deletion fallback')
        sessions.forEach((session, index) => {
          setTimeout(() => {
            console.log(`🗑️ SIDEBAR: Deleting session ${index + 1}/${sessions.length}:`, session.id)
            deleteSession(session.id)
          }, index * 50) // Stagger deletions
        })
      }
    }
  }

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: 280,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: 280,
          boxSizing: 'border-box',
          backgroundColor: 'background.paper',
          borderRight: 1,
          borderColor: 'divider',
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
        },
      }}
    >
      <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 3, mt: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, color: '#1976d2' }}>
            💬 Chat History
          </Typography>
        </Box>

        <Box sx={{ mb: 3, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {/* New Chat Button */}
          <Box
            onClick={handleNewChat}
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 1,
              p: 2,
              borderRadius: 2,
              cursor: 'pointer',
              background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
              color: 'white',
              width: '100%',
              minHeight: '48px',
              '&:hover': {
                background: 'linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)',
                transform: 'translateY(-1px)',
                boxShadow: '0 4px 12px rgba(25, 118, 210, 0.3)',
              },
              transition: 'all 0.2s ease',
            }}
          >
            <AddIcon sx={{ fontSize: 20 }} />
            <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '0.9rem' }}>
              New Chat
            </Typography>
          </Box>
          
          {/* Delete All Chats Button */}
          {sessions.length > 0 && (
            <Box
              onClick={handleDeleteAllChats}
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 1,
                p: 1.5,
                borderRadius: 2,
                cursor: 'pointer',
                background: 'transparent',
                color: 'error.main',
                border: '1px solid',
                borderColor: 'error.main',
                width: '100%',
                minHeight: '40px',
                opacity: 0.8,
                '&:hover': {
                  background: 'rgba(244, 67, 54, 0.1)',
                  transform: 'translateY(-1px)',
                  opacity: 1,
                  boxShadow: '0 2px 8px rgba(244, 67, 54, 0.2)',
                },
                transition: 'all 0.2s ease',
              }}
            >
              <DeleteIcon sx={{ fontSize: 18 }} />
              <Typography variant="caption" sx={{ fontWeight: 600, fontSize: '0.8rem' }}>
                Delete All ({sessions.length})
              </Typography>
            </Box>
          )}
        </Box>

        <Divider sx={{ mb: 2 }} />

        <List sx={{ flex: 1, overflow: 'auto', py: 0 }}>
          {sessions.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <HistoryIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
              <Typography variant="body2" color="text.secondary">
                No chat history yet
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Start a conversation to see your history here
              </Typography>
            </Box>
          ) : (
            sessions.map((session) => (
              <ListItem
                key={session.id}
                disablePadding
                sx={{ mb: 1 }}
              >
                <ListItemButton
                  selected={session.id === currentSessionId}
                  onClick={() => handleSessionSelect(session.id)}
                  sx={{
                    borderRadius: 2,
                    '&.Mui-selected': {
                      background: 'rgba(25, 118, 210, 0.1)',
                      '&:hover': {
                        background: 'rgba(25, 118, 210, 0.15)',
                      },
                    },
                    '&:hover': {
                      background: 'rgba(0,0,0,0.05)',
                    },
                  }}
                >
                  <ListItemIcon>
                    <ChatIcon fontSize="small" />
                  </ListItemIcon>
                  
                  <ListItemText
                    primary={
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: session.id === currentSessionId ? 600 : 400,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {session.title}
                      </Typography>
                    }
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                        <Typography variant="caption" color="text.secondary">
                          {session.updatedAt ? format(new Date(session.updatedAt), 'MMM d, h:mm a') : 'Unknown'}
                        </Typography>
                        <Chip
                          label={`${session.messages.length} messages`}
                          size="small"
                          variant="outlined"
                          sx={{ height: 20, fontSize: '0.7rem' }}
                        />
                      </Box>
                    }
                  />

                  <IconButton
                    size="small"
                    onClick={(e) => {
                      console.log('Delete button clicked for session:', session.id)
                      e.preventDefault()
                      e.stopPropagation()
                      
                      // Force immediate UI feedback
                      const button = e.currentTarget
                      button.style.transform = 'scale(0.9)'
                      button.style.opacity = '0.5'
                      
                      setTimeout(() => {
                        handleDeleteSession(session.id, e)
                        button.style.transform = ''
                        button.style.opacity = ''
                      }, 100)
                    }}
                    sx={{
                      opacity: 0.8,
                      ml: 1,
                      minWidth: '32px',
                      minHeight: '32px',
                      '&:hover': {
                        opacity: 1,
                        background: 'rgba(244, 67, 54, 0.15)',
                        color: 'error.main',
                        transform: 'scale(1.1)',
                      },
                      '&:active': {
                        transform: 'scale(0.95)',
                        background: 'rgba(244, 67, 54, 0.2)',
                      },
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </ListItemButton>
              </ListItem>
            ))
          )}
        </List>

        {/* Footer */}
        <Box sx={{ 
          mt: 'auto', 
          pt: 2, 
          pb: 1,
          borderTop: 1, 
          borderColor: 'divider',
          backgroundColor: 'action.hover',
          mx: -2,
          px: 2,
          borderRadius: '8px 8px 0 0'
        }}>
          <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center', display: 'block', fontWeight: 500 }}>
            Health Chatbot v1.0
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center', display: 'block', fontSize: '0.7rem' }}>
            Powered by AI & RAG Technology
          </Typography>
        </Box>
      </Box>
    </Drawer>
  )
}

export default Sidebar
