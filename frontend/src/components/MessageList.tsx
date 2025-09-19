import React, { useEffect, useRef } from 'react'
import { Box, Fade } from '@mui/material'
import { useChatStore } from '../store/chatStore'
import MessageBubble from './MessageBubble'

const MessageList: React.FC = () => {
  const { messages, isTyping, currentSessionId, createNewSession } = useChatStore()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  

  // Ensure we have a session
  useEffect(() => {
    if (!currentSessionId) {
      createNewSession()
    }
  }, [currentSessionId, createNewSession])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  return (
    <Box
      sx={{
        flex: 1,
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        minHeight: 'auto',
      }}
    >

      {/* Messages */}
      {messages.map((message, index) => (
        <Fade key={message.id} in timeout={300}>
          <Box sx={{ 
            mb: index === messages.length - 1 ? 0 : 1,
            '&:first-of-type': { mt: 1 }
          }}>
            <MessageBubble
              message={message}
              isLast={index === messages.length - 1}
            />
          </Box>
        </Fade>
      ))}

      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </Box>
  )
}

export default MessageList
