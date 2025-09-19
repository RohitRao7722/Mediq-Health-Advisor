import React from 'react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight, oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { Box, useTheme } from '@mui/material'
import { useChatStore } from '../store/chatStore'

interface MarkdownRendererProps {
  content: string
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  const theme = useTheme()
  const { settings } = useChatStore()
  
  const isDarkMode = settings.theme === 'dark' || 
    (settings.theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches)

  return (
    <Box
      sx={{
        '& h1, & h2, & h3, & h4, & h5, & h6': {
          marginTop: 2,
          marginBottom: 1,
          fontWeight: 600,
          color: 'text.primary',
        },
        '& h1': { fontSize: '1.5rem' },
        '& h2': { fontSize: '1.3rem' },
        '& h3': { fontSize: '1.1rem' },
        '& h4': { fontSize: '1rem' },
        '& h5': { fontSize: '0.9rem' },
        '& h6': { fontSize: '0.8rem' },
        '& p': {
          marginBottom: 1,
          lineHeight: 1.6,
        },
        '& ul, & ol': {
          marginBottom: 1,
          paddingLeft: 2,
        },
        '& li': {
          marginBottom: 0.5,
        },
        '& blockquote': {
          margin: '16px 0',
          padding: '8px 16px',
          borderLeft: '4px solid',
          borderLeftColor: 'primary.main',
          background: 'rgba(25, 118, 210, 0.05)',
          fontStyle: 'italic',
        },
        '& code': {
          background: 'rgba(0,0,0,0.05)',
          padding: '2px 4px',
          borderRadius: '4px',
          fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
          fontSize: '0.9em',
        },
        '& pre': {
          margin: '16px 0',
          borderRadius: '8px',
          overflow: 'auto',
        },
        '& table': {
          width: '100%',
          borderCollapse: 'collapse',
          margin: '16px 0',
          fontSize: '0.9em',
        },
        '& th, & td': {
          border: '1px solid',
          borderColor: 'divider',
          padding: '8px 12px',
          textAlign: 'left',
        },
        '& th': {
          background: 'rgba(0,0,0,0.05)',
          fontWeight: 600,
        },
        '& tr:nth-of-type(even)': {
          background: 'rgba(0,0,0,0.02)',
        },
        '& a': {
          color: 'primary.main',
          textDecoration: 'none',
          '&:hover': {
            textDecoration: 'underline',
          },
        },
        '& img': {
          maxWidth: '100%',
          height: 'auto',
          borderRadius: '8px',
          margin: '8px 0',
        },
        '& .katex-display': {
          margin: '16px 0',
        },
        '& .katex': {
          fontSize: '1.1em',
        },
      }}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '')
            const language = match ? match[1] : ''
            
            if (!inline && language) {
              return (
                <SyntaxHighlighter
                  style={isDarkMode ? oneDark : oneLight}
                  language={language}
                  PreTag="div"
                  customStyle={{
                    margin: '16px 0',
                    borderRadius: '8px',
                    fontSize: '0.9em',
                  }}
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              )
            }
            
            return (
              <code className={className} {...props}>
                {children}
              </code>
            )
          },
          table({ children }) {
            return (
              <Box sx={{ overflow: 'auto', margin: '16px 0' }}>
                <table className="markdown-table">{children}</table>
              </Box>
            )
          },
          blockquote({ children }) {
            return (
              <Box
                component="blockquote"
                sx={{
                  margin: '16px 0',
                  padding: '8px 16px',
                  borderLeft: '4px solid',
                  borderLeftColor: 'primary.main',
                  background: 'rgba(25, 118, 210, 0.05)',
                  fontStyle: 'italic',
                  borderRadius: '0 8px 8px 0',
                }}
              >
                {children}
              </Box>
            )
          },
          h1({ children }) {
            return (
              <Box component="h1" sx={{ 
                fontSize: '1.5rem', 
                fontWeight: 600, 
                margin: '16px 0 8px 0',
                color: 'text.primary',
              }}>
                {children}
              </Box>
            )
          },
          h2({ children }) {
            return (
              <Box component="h2" sx={{ 
                fontSize: '1.3rem', 
                fontWeight: 600, 
                margin: '16px 0 8px 0',
                color: 'text.primary',
              }}>
                {children}
              </Box>
            )
          },
          h3({ children }) {
            return (
              <Box component="h3" sx={{ 
                fontSize: '1.1rem', 
                fontWeight: 600, 
                margin: '12px 0 6px 0',
                color: 'text.primary',
              }}>
                {children}
              </Box>
            )
          },
          p({ children }) {
            return (
              <Box component="p" sx={{ 
                margin: '0 0 8px 0',
                lineHeight: 1.6,
              }}>
                {children}
              </Box>
            )
          },
          ul({ children }) {
            return (
              <Box component="ul" sx={{ 
                margin: '8px 0',
                paddingLeft: '24px',
              }}>
                {children}
              </Box>
            )
          },
          ol({ children }) {
            return (
              <Box component="ol" sx={{ 
                margin: '8px 0',
                paddingLeft: '24px',
              }}>
                {children}
              </Box>
            )
          },
          li({ children }) {
            return (
              <Box component="li" sx={{ 
                margin: '4px 0',
                lineHeight: 1.5,
              }}>
                {children}
              </Box>
            )
          },
          a({ href, children }) {
            return (
              <Box
                component="a"
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                sx={{
                  color: 'primary.main',
                  textDecoration: 'none',
                  '&:hover': {
                    textDecoration: 'underline',
                  },
                }}
              >
                {children}
              </Box>
            )
          },
          strong({ children }) {
            return (
              <Box component="strong" sx={{ fontWeight: 600 }}>
                {children}
              </Box>
            )
          },
          em({ children }) {
            return (
              <Box component="em" sx={{ fontStyle: 'italic' }}>
                {children}
              </Box>
            )
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </Box>
  )
}

export default MarkdownRenderer

