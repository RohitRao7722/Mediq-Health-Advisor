import React from 'react'
import { Box, Typography } from '@mui/material'

const TypingIndicator: React.FC = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'flex-start',
        mb: 2,
      }}
    >
      <Box
        sx={{
          background: 'white',
          borderRadius: '18px 18px 18px 4px',
          p: 2,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          border: '1px solid #e0e0e0',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 0.5,
          }}
        >
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: '#1976d2',
              animation: 'typing 1.4s infinite',
            }}
          />
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: '#1976d2',
              animation: 'typing 1.4s infinite 0.2s',
            }}
          />
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: '#1976d2',
              animation: 'typing 1.4s infinite 0.4s',
            }}
          />
        </Box>
        
        <Typography variant="body2" color="text.secondary">
          AI is thinking...
        </Typography>
      </Box>
    </Box>
  )
}

export default TypingIndicator

