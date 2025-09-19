import React from 'react'
import {
  Box,
  Paper,
  Typography,
  Chip,
  useTheme,
  useMediaQuery,
} from '@mui/material'
import {
  LocalHospital as HospitalIcon,
  Psychology as PsychologyIcon,
  Favorite as HeartIcon,
  Warning as WarningIcon,
  Science as ScienceIcon,
} from '@mui/icons-material'

const WelcomeMessage: React.FC = () => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))

  const features = [
    { icon: <HospitalIcon />, label: 'Symptom Analysis', color: 'primary' },
    { icon: <PsychologyIcon />, label: 'Mental Health', color: 'secondary' },
    { icon: <HeartIcon />, label: 'Preventive Care', color: 'error' },
    { icon: <ScienceIcon />, label: 'Medical Knowledge', color: 'info' },
  ]

  const exampleQuestions = [
    "What are the symptoms of diabetes?",
    "How to manage stress and anxiety?",
    "What should I do if I have chest pain?",
    "How to maintain a healthy lifestyle?",
    "What are the warning signs of a heart attack?",
  ]

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'flex-start',
        minHeight: 'auto',
        p: { xs: 1, sm: 2 },
        pt: { xs: 2, sm: 4 },
      }}
    >
      <Paper
        elevation={8}
        sx={{
          maxWidth: { xs: '100%', sm: 600, md: 700 },
          width: '100%',
          p: { xs: 3, sm: 4, md: 5 },
          textAlign: 'center',
          background: theme.palette.mode === 'dark' 
            ? 'rgba(30, 30, 30, 0.98)' 
            : 'rgba(255,255,255,0.98)',
          backdropFilter: 'blur(20px)',
          borderRadius: 4,
          border: theme.palette.mode === 'dark' 
            ? '1px solid rgba(255,255,255,0.1)' 
            : '1px solid rgba(0,0,0,0.05)',
          boxShadow: theme.palette.mode === 'dark' 
            ? '0 20px 60px rgba(0,0,0,0.4)' 
            : '0 20px 60px rgba(0,0,0,0.1)',
        }}
      >
        {/* Header */}
        <Box sx={{ mb: { xs: 2, sm: 3 } }}>
          <Typography 
            variant={isMobile ? 'h4' : 'h3'}
            gutterBottom 
            sx={{ 
              fontWeight: 800, 
              background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: { xs: 1, sm: 2 },
            }}
          >
            🏥 Health Chatbot
          </Typography>
          <Typography 
            variant={isMobile ? 'h6' : 'h5'}
            color="text.secondary" 
            sx={{ mb: { xs: 2, sm: 3 }, fontWeight: 500 }}
          >
            Your AI-powered medical assistant
          </Typography>
          <Typography 
            variant="body1" 
            color="text.secondary" 
            sx={{ 
              lineHeight: 1.6, 
              maxWidth: { xs: '100%', sm: 500 }, 
              mx: 'auto',
              fontSize: { xs: '0.9rem', sm: '1rem' }
            }}
          >
            Ask me about health, symptoms, treatments, and wellness. I can help you understand 
            medical information and provide guidance based on authoritative health sources.
          </Typography>
        </Box>

        {/* Features */}
        <Box sx={{ mb: { xs: 2, sm: 3 } }}>
          <Typography 
            variant="subtitle1" 
            gutterBottom 
            sx={{ fontWeight: 600, fontSize: { xs: '0.9rem', sm: '1rem' } }}
          >
            What I can help with:
          </Typography>
          <Box sx={{ 
            display: 'flex', 
            flexWrap: 'wrap', 
            gap: { xs: 0.5, sm: 1 }, 
            justifyContent: 'center' 
          }}>
            {features.map((feature, index) => (
              <Chip
                key={index}
                icon={feature.icon}
                label={feature.label}
                color={feature.color as any}
                variant="outlined"
                size={isMobile ? 'small' : 'medium'}
                sx={{ mb: 1 }}
              />
            ))}
          </Box>
        </Box>

        {/* Example Questions */}
        <Box sx={{ mb: { xs: 2, sm: 3 } }}>
          <Typography 
            variant="h6" 
            gutterBottom 
            sx={{ 
              fontWeight: 700, 
              mb: { xs: 2, sm: 3 },
              fontSize: { xs: '1.1rem', sm: '1.25rem' }
            }}
          >
            💡 Try asking:
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: { xs: 1, sm: 1.5 } }}>
            {exampleQuestions.slice(0, isMobile ? 3 : 5).map((question, index) => (
              <Box
                key={index}
                sx={{
                  p: { xs: 1.5, sm: 2 },
                  background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.05) 0%, rgba(25, 118, 210, 0.02) 100%)',
                  borderRadius: 2,
                  border: '1px solid rgba(25, 118, 210, 0.1)',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.1) 0%, rgba(25, 118, 210, 0.05) 100%)',
                    borderColor: 'rgba(25, 118, 210, 0.2)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 12px rgba(25, 118, 210, 0.15)',
                  },
                }}
                onClick={() => {
                  // This would trigger a message send
                  console.log('Example question clicked:', question)
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 500,
                    color: 'text.primary',
                    fontSize: { xs: '0.85rem', sm: '0.95rem' },
                    '&:hover': {
                      color: 'primary.main',
                    },
                  }}
                >
                  💬 {question}
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>

        {/* Disclaimer */}
        <Box
          sx={{
            p: { xs: 2, sm: 3 },
            background: 'linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 193, 7, 0.05) 100%)',
            border: '1px solid rgba(255, 193, 7, 0.3)',
            borderRadius: 3,
            textAlign: 'left',
            boxShadow: '0 4px 12px rgba(255, 193, 7, 0.1)',
          }}
        >
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: { xs: 1, sm: 1.5 }, 
            mb: { xs: 1, sm: 2 },
            flexDirection: { xs: 'column', sm: 'row' },
            textAlign: { xs: 'center', sm: 'left' }
          }}>
            <WarningIcon color="warning" fontSize={isMobile ? 'small' : 'medium'} />
            <Typography 
              variant={isMobile ? 'subtitle2' : 'h6'}
              color="warning.main" 
              sx={{ fontWeight: 700 }}
            >
              ⚠️ Important Medical Disclaimer
            </Typography>
          </Box>
          <Typography 
            variant="body2" 
            color="text.secondary" 
            sx={{ 
              lineHeight: 1.5, 
              fontSize: { xs: '0.8rem', sm: '0.875rem' }
            }}
          >
            This AI assistant provides general health information only. It is <strong>NOT</strong> a substitute 
            for professional medical advice, diagnosis, or treatment. Always consult with 
            qualified healthcare professionals for medical concerns. In case of medical emergency, 
            call emergency services immediately.
          </Typography>
        </Box>

        {/* Footer */}
        <Box sx={{ 
          mt: { xs: 2, sm: 3 }, 
          pt: { xs: 2, sm: 3 }, 
          borderTop: '1px solid', 
          borderColor: 'divider' 
        }}>
          <Typography 
            variant="body2" 
            color="text.secondary" 
            sx={{ 
              fontWeight: 500,
              fontSize: { xs: '0.75rem', sm: '0.875rem' }
            }}
          >
            🚀 Powered by advanced AI and authoritative health sources
          </Typography>
        </Box>
      </Paper>
    </Box>
  )
}

export default WelcomeMessage
