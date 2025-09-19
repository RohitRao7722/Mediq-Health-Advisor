import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Collapse,
  Chip,
  Tooltip,
  useTheme,
  useMediaQuery,
} from '@mui/material'
import {
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  ContentCopy as CopyIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material'
import { useChatStore } from '../store/chatStore'
import { Message } from '../store/chatStore'
import MarkdownRenderer from './MarkdownRenderer'
import SourceCitations from './SourceCitations'
import { toast } from 'react-hot-toast'

interface MessageBubbleProps {
  message: Message
  isLast: boolean
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isLast }) => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [showSources, setShowSources] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  
  const { updateMessage, deleteMessage, rateMessage } = useChatStore()

  const isUser = message.role === 'user'
  const isAssistant = message.role === 'assistant'
  const hasSources = message.sources && message.sources.length > 0
  const isLongMessage = message.content.length > 500
  

  const handleRating = (rating: 'positive' | 'negative') => {
    rateMessage(message.id, rating)
    toast.success(`Thank you for your feedback!`)
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    toast.success('Message copied to clipboard')
  }

  const handleRegenerate = () => {
    toast('Message regeneration feature coming soon!', {
      icon: '🔄',
      duration: 2000
    })
  }

  const handleDelete = () => {
    deleteMessage(message.id)
    toast.success('Message deleted')
  }

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded)
  }

  const toggleSources = () => {
    setShowSources(!showSources)
  }

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Paper
        elevation={isUser ? 6 : 4}
        sx={{
          maxWidth: isMobile ? '90%' : '80%',
          minWidth: '200px',
          p: 3,
          borderRadius: isUser ? '24px 24px 8px 24px' : '24px 24px 24px 8px',
          background: isUser 
            ? 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)'
            : theme.palette.mode === 'dark'
              ? 'linear-gradient(135deg, #2a2a2a 0%, #3a3a3a 100%)'
              : 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
          color: isUser 
            ? '#ffffff' 
            : theme.palette.mode === 'dark' 
              ? '#ffffff' 
              : '#1a1a1a',
          position: 'relative',
          border: isUser ? 'none' : '1px solid rgba(0,0,0,0.05)',
          boxShadow: isUser 
            ? '0 6px 24px rgba(25, 118, 210, 0.3)' 
            : '0 4px 20px rgba(0,0,0,0.08)',
          '&:hover': {
            boxShadow: isUser 
              ? '0 8px 32px rgba(25, 118, 210, 0.4)' 
              : '0 8px 32px rgba(0,0,0,0.12)',
            transform: 'translateY(-2px)',
          },
          transition: 'all 0.3s ease',
        }}
      >
        {/* Message Content */}
        <Box sx={{ mb: 1, '& > *:last-child': { marginBottom: 0 } }}>
          {isAssistant ? (
            <MarkdownRenderer content={message.content} />
          ) : (
            <Typography 
              variant="body1" 
              sx={{ 
                whiteSpace: 'pre-wrap',
                lineHeight: 1.6,
                wordBreak: 'break-word'
              }}
            >
              {message.content}
            </Typography>
          )}
        </Box>

        {/* Error State */}
        {message.error && (
          <Box
            sx={{
              mt: 1,
              p: 1,
              background: 'rgba(244, 67, 54, 0.1)',
              border: '1px solid rgba(244, 67, 54, 0.3)',
              borderRadius: 1,
            }}
          >
            <Typography variant="caption" color="error">
              Error: {message.error}
            </Typography>
          </Box>
        )}

        {/* Streaming Indicator */}
        {message.isStreaming && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: theme.palette.primary.main,
                animation: 'pulse 1.5s infinite',
              }}
            />
            <Typography variant="caption" color="text.secondary">
              AI is thinking...
            </Typography>
          </Box>
        )}

        {/* Message Metadata */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mt: 1,
            pt: 1,
            borderTop: '1px solid rgba(0,0,0,0.1)',
          }}
        >
          <Typography variant="caption" color="text.secondary">
            {new Date(message.timestamp).toLocaleTimeString()}
          </Typography>

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            {/* Copy Button */}
            <Tooltip title="Copy message">
              <IconButton
                size="small"
                onClick={handleCopy}
                sx={{ color: 'text.secondary' }}
              >
                <CopyIcon fontSize="small" />
              </IconButton>
            </Tooltip>

            {/* Expand/Collapse Button for long messages */}
            {isLongMessage && (
              <Tooltip title={isExpanded ? 'Show less' : 'Show more'}>
                <IconButton
                  size="small"
                  onClick={toggleExpanded}
                  sx={{ color: 'text.secondary' }}
                >
                  {isExpanded ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
                </IconButton>
              </Tooltip>
            )}

            {/* Regenerate Button for assistant messages */}
            {isAssistant && !message.isStreaming && (
              <Tooltip title="Regenerate response">
                <IconButton
                  size="small"
                  onClick={handleRegenerate}
                  sx={{ color: 'text.secondary' }}
                >
                  <RefreshIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}

            {/* Delete Button */}
            <Tooltip title="Delete message">
              <IconButton
                size="small"
                onClick={handleDelete}
                sx={{ color: 'text.secondary' }}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Rating Buttons for Assistant Messages */}
        {isAssistant && !message.isStreaming && (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              gap: 1,
              mt: 1,
              pt: 1,
              borderTop: '1px solid rgba(0,0,0,0.1)',
            }}
          >
            <Tooltip title="This response was helpful">
              <IconButton
                size="small"
                onClick={() => handleRating('positive')}
                sx={{
                  color: message.rating === 'positive' ? 'success.main' : 'text.secondary',
                }}
              >
                <ThumbUpIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="This response was not helpful">
              <IconButton
                size="small"
                onClick={() => handleRating('negative')}
                sx={{
                  color: message.rating === 'negative' ? 'error.main' : 'text.secondary',
                }}
              >
                <ThumbDownIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        )}

        {/* Sources Section */}
        {isAssistant && hasSources && (
          <Box sx={{ mt: 2 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                mb: 1,
                cursor: 'pointer',
                '&:hover': { opacity: 0.8 },
              }}
              onClick={toggleSources}
            >
              <Typography variant="caption" fontWeight="medium">
                Sources ({message.sources?.length})
              </Typography>
              {showSources ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
            </Box>

            <Collapse in={showSources}>
              <SourceCitations sources={message.sources || []} />
            </Collapse>
          </Box>
        )}
      </Paper>
    </Box>
  )
}

export default MessageBubble
