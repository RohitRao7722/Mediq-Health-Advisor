import React from 'react'
import { Box, Typography, CircularProgress } from '@mui/material'

const LoadingScreen: React.FC = () => {
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
      <Box
        sx={{
          background: 'rgba(255,255,255,0.1)',
          borderRadius: 3,
          p: 4,
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255,255,255,0.2)',
        }}
      >
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
          🏥 Health Chatbot
        </Typography>
        
        <CircularProgress
          size={60}
          thickness={4}
          sx={{
            color: 'white',
            mb: 3,
          }}
        />
        
        <Typography variant="h6" gutterBottom>
          Initializing AI Assistant
        </Typography>
        
        <Typography variant="body2" sx={{ opacity: 0.9, maxWidth: 400 }}>
          Loading medical knowledge base and connecting to AI services...
        </Typography>
      </Box>
    </Box>
  )
}

export default LoadingScreen

