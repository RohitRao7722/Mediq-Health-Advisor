import React from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  useTheme,
} from '@mui/material'
import {
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import { useChatStore } from '../store/chatStore'

const Header: React.FC = () => {
  const theme = useTheme()
  
  const {
    toggleSettings,
    clearSession,
  } = useChatStore()

  const handleNewChat = () => {
    clearSession()
  }

  return (
    <AppBar
      position="fixed"
      sx={{
        backgroundColor: 'background.paper',
        backdropFilter: 'blur(10px)',
        borderBottom: 1,
        borderColor: 'divider',
        color: 'text.primary',
        zIndex: theme.zIndex.drawer + 1,
        boxShadow: theme.palette.mode === 'dark' 
          ? '0 2px 8px rgba(0,0,0,0.3)' 
          : '0 2px 8px rgba(0,0,0,0.1)',
      }}
    >
      <Toolbar sx={{ pl: { xs: 2, md: 2 } }}>

        {/* Title */}
        <Typography
          variant="h6"
          component="div"
          sx={{
            flexGrow: 1,
            fontWeight: 600,
            background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          🏥 Health Chatbot
        </Typography>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 1 }}>
          {/* New Chat Button */}
          <IconButton
            onClick={handleNewChat}
            title="Start new chat"
            sx={{
              color: 'text.primary',
              backgroundColor: 'transparent',
              '&:hover': {
                backgroundColor: 'action.hover',
                color: 'primary.main',
                transform: 'scale(1.05)',
              },
              transition: 'all 0.2s ease',
            }}
          >
            <RefreshIcon />
          </IconButton>

          {/* Settings Button */}
          <IconButton
            onClick={toggleSettings}
            title="Settings"
            sx={{
              color: 'text.primary',
              backgroundColor: 'transparent',
              '&:hover': {
                backgroundColor: 'action.hover',
                color: 'primary.main',
                transform: 'scale(1.05)',
              },
              transition: 'all 0.2s ease',
            }}
          >
            <SettingsIcon />
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default Header

