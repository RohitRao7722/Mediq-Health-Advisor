import React from 'react'
import { Box, Chip, Fade } from '@mui/material'
import { useChatStore } from '../store/chatStore'

const ConnectionStatus: React.FC = () => {
  const { isConnected } = useChatStore()

  return (
    <Fade in={!isConnected}>
      <Box
        sx={{
          position: 'fixed',
          top: 16,
          right: 16,
          zIndex: 1000,
        }}
      >
        <Chip
          label={isConnected ? 'Connected' : 'Disconnected'}
          color={isConnected ? 'success' : 'error'}
          variant="filled"
          sx={{
            fontWeight: 600,
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
          }}
        />
      </Box>
    </Fade>
  )
}

export default ConnectionStatus

