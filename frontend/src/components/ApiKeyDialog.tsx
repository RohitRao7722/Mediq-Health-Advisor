import React, { useState } from 'react'
import { apiService } from '../services/api'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  Link,
  Divider,
  IconButton,
  InputAdornment,
} from '@mui/material'
import {
  Visibility,
  VisibilityOff,
  Key as KeyIcon,
  Info as InfoIcon,
} from '@mui/icons-material'

interface ApiKeyDialogProps {
  open: boolean
  onApiKeySet: (apiKey: string | null) => void
}

const ApiKeyDialog: React.FC<ApiKeyDialogProps> = ({ open, onApiKeySet }) => {
  const [apiKey, setApiKey] = useState('')
  const [showApiKey, setShowApiKey] = useState(false)
  const [isValidating, setIsValidating] = useState(false)

  const handleUseOwnKey = async () => {
    if (!apiKey.trim()) {
      return
    }

    setIsValidating(true)
    
    try {
      // Validate the API key
      const isValid = await apiService.validateApiKey(apiKey.trim())
      
      if (isValid) {
        onApiKeySet(apiKey.trim())
      } else {
        alert('Invalid API key. Please check your key and try again.')
      }
    } catch (error) {
      console.error('API key validation error:', error)
      // If validation fails, still allow the key to be used (backend might not support validation yet)
      onApiKeySet(apiKey.trim())
    } finally {
      setIsValidating(false)
    }
  }

  const handleUseDefault = () => {
    onApiKeySet(null) // null means use internal/default key
  }

  const handleToggleVisibility = () => {
    setShowApiKey(!showApiKey)
  }

  return (
    <Dialog
      open={open}
      maxWidth="md"
      fullWidth
      disableEscapeKeyDown
      sx={{
        '& .MuiDialog-paper': {
          borderRadius: 3,
          p: 1,
        },
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <KeyIcon color="primary" sx={{ fontSize: 32 }} />
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 600 }}>
              Welcome to Health Chatbot
            </Typography>
            <Typography variant="subtitle2" color="text.secondary">
              Configure your API access to get started
            </Typography>
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pt: 2 }}>
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>Choose your API option:</strong> Use your own Groq API key for unlimited access, 
            or use our shared key with rate limits.
          </Typography>
        </Alert>

        {/* Option 1: Use Own API Key */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <InfoIcon color="primary" />
            Option 1: Use Your Own Groq API Key (Recommended)
          </Typography>
          
          <Box sx={{ pl: 4 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              • Unlimited requests and faster responses<br/>
              • Your data stays private<br/>
              • Better performance during peak hours
            </Typography>

            <TextField
              fullWidth
              label="Enter your Groq API Key"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              type={showApiKey ? 'text' : 'password'}
              placeholder="gsk_..."
              sx={{ mb: 2 }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={handleToggleVisibility}
                      edge="end"
                      size="small"
                    >
                      {showApiKey ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Typography variant="caption" color="text.secondary">
              Don't have a Groq API key?{' '}
              <Link 
                href="https://console.groq.com/keys" 
                target="_blank" 
                rel="noopener noreferrer"
              >
                Get one free here
              </Link>
              {' '}(takes 2 minutes)
            </Typography>
          </Box>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Option 2: Use Default Key */}
        <Box>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <InfoIcon color="secondary" />
            Option 2: Use Shared API Key
          </Typography>
          
          <Box sx={{ pl: 4 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              • Quick setup - no registration needed<br/>
              • Rate limited during peak hours<br/>
              • Shared with other users
            </Typography>
          </Box>
        </Box>

        <Alert severity="warning" sx={{ mt: 3 }}>
          <Typography variant="body2">
            <strong>Privacy Note:</strong> Your conversations are not stored on our servers. 
            API keys are only stored locally in your browser.
          </Typography>
        </Alert>
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 2 }}>
        <Button
          onClick={handleUseDefault}
          variant="outlined"
          size="large"
          sx={{ minWidth: 160 }}
        >
          Use Shared Key
        </Button>
        <Button
          onClick={handleUseOwnKey}
          variant="contained"
          size="large"
          disabled={!apiKey.trim() || isValidating}
          sx={{ minWidth: 160 }}
        >
          {isValidating ? 'Validating...' : 'Use My Key'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default ApiKeyDialog
