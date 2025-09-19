import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Chip,
  Collapse,
  IconButton,
  Tooltip,
  useTheme,
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  ContentCopy as CopyIcon,
  OpenInNew as OpenInNewIcon,
  Info as InfoIcon,
} from '@mui/icons-material'
import { Source } from '../store/chatStore'
import { toast } from 'react-hot-toast'

interface SourceCitationsProps {
  sources: Source[]
}

const SourceCitations: React.FC<SourceCitationsProps> = ({ sources }) => {
  const theme = useTheme()
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set())

  const toggleSource = (sourceId: string) => {
    const newExpanded = new Set(expandedSources)
    if (newExpanded.has(sourceId)) {
      newExpanded.delete(sourceId)
    } else {
      newExpanded.add(sourceId)
    }
    setExpandedSources(newExpanded)
  }

  const copySourceContent = (content: string) => {
    navigator.clipboard.writeText(content)
    toast.success('Source content copied to clipboard')
  }

  const getRelevanceColor = (score: number) => {
    if (score < 0.3) return 'success'
    if (score < 0.6) return 'warning'
    return 'error'
  }

  const getRelevanceLabel = (score: number) => {
    if (score < 0.3) return 'High Relevance'
    if (score < 0.6) return 'Medium Relevance'
    return 'Low Relevance'
  }

  const formatFileName = (source: string) => {
    const fileName = source.split('/').pop() || source
    return fileName.replace(/\.(csv|pdf|txt|json|html)$/, '')
  }

  const getFileTypeIcon = (source: string) => {
    if (source.includes('.csv')) return '📊'
    if (source.includes('.pdf')) return '📄'
    if (source.includes('.txt')) return '📝'
    if (source.includes('.json')) return '🔧'
    if (source.includes('.html')) return '🌐'
    return '📁'
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
      {sources.map((source, index) => {
        const isExpanded = expandedSources.has(source.id)
        const relevanceColor = getRelevanceColor(source.relevanceScore)
        const relevanceLabel = getRelevanceLabel(source.relevanceScore)
        const fileName = formatFileName(source.metadata.source || 'Unknown')
        const fileIcon = getFileTypeIcon(source.metadata.source || '')

        return (
          <Paper
            key={source.id}
            elevation={1}
            sx={{
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 2,
              overflow: 'hidden',
              transition: 'all 0.2s ease',
              '&:hover': {
                boxShadow: theme.shadows[2],
                borderColor: 'primary.main',
              },
            }}
          >
            {/* Source Header */}
            <Box
              sx={{
                p: 2,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: 'rgba(0,0,0,0.02)',
                '&:hover': {
                  background: 'rgba(0,0,0,0.05)',
                },
              }}
              onClick={() => toggleSource(source.id)}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
                <Typography variant="h6" sx={{ fontSize: '1.2em' }}>
                  {fileIcon}
                </Typography>
                
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography
                    variant="subtitle2"
                    sx={{
                      fontWeight: 600,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {source.title || fileName}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                    <Chip
                      label={relevanceLabel}
                      size="small"
                      color={relevanceColor as any}
                      variant="outlined"
                    />
                    
                    <Typography variant="caption" color="text.secondary">
                      Score: {source.relevanceScore.toFixed(3)}
                    </Typography>
                    
                    {source.metadata.chunk_index !== undefined && (
                      <Typography variant="caption" color="text.secondary">
                        Chunk {source.metadata.chunk_index + 1}/{source.metadata.total_chunks}
                      </Typography>
                    )}
                  </Box>
                </Box>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Tooltip title="Copy source content">
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation()
                      copySourceContent(source.content)
                    }}
                    sx={{ color: 'text.secondary' }}
                  >
                    <CopyIcon fontSize="small" />
                  </IconButton>
                </Tooltip>

                {source.url && (
                  <Tooltip title="Open source">
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation()
                        window.open(source.url, '_blank')
                      }}
                      sx={{ color: 'text.secondary' }}
                    >
                      <OpenInNewIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}

                <IconButton size="small" sx={{ color: 'text.secondary' }}>
                  {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </IconButton>
              </Box>
            </Box>

            {/* Source Content */}
            <Collapse in={isExpanded}>
              <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    mb: 1,
                    p: 1,
                    background: 'rgba(25, 118, 210, 0.05)',
                    borderRadius: 1,
                  }}
                >
                  <InfoIcon fontSize="small" color="primary" />
                  <Typography variant="caption" color="primary.main" fontWeight="medium">
                    Retrieved Content
                  </Typography>
                </Box>

                <Box
                  sx={{
                    background: 'rgba(0,0,0,0.02)',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    p: 2,
                    fontFamily: 'monospace',
                    fontSize: '0.9em',
                    lineHeight: 1.5,
                    whiteSpace: 'pre-wrap',
                    maxHeight: '200px',
                    overflow: 'auto',
                  }}
                >
                  {source.content}
                </Box>

                {/* Source Metadata */}
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight="medium">
                    Source Details:
                  </Typography>
                  
                  <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {source.metadata.source && (
                      <Chip
                        label={`File: ${fileName}`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                    
                    {source.metadata.file_type && (
                      <Chip
                        label={`Type: ${source.metadata.file_type.toUpperCase()}`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                    
                    {source.metadata.chunk_size && (
                      <Chip
                        label={`Size: ${source.metadata.chunk_size} chars`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>
                </Box>
              </Box>
            </Collapse>
          </Paper>
        )
      })}

      {/* Footer */}
      <Box
        sx={{
          mt: 1,
          p: 1,
          background: 'rgba(0,0,0,0.02)',
          borderRadius: 1,
          textAlign: 'center',
        }}
      >
        <Typography variant="caption" color="text.secondary">
          Sources are ranked by relevance to your question. Click to expand and view details.
        </Typography>
      </Box>
    </Box>
  )
}

export default SourceCitations

