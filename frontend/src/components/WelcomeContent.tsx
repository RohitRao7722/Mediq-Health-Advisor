import React from 'react'
import {
  Box,
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

const WelcomeContent: React.FC = () => {
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
        textAlign: 'center',
        p: { xs: 2, sm: 3 },
        maxWidth: 800,
        mx: 'auto',
      }}
    >
      {/* Header */}
      <Box sx={{ mb: { xs: 2, sm: 3 } }}>
        <Typography 
          variant={isMobile ? 'h5' : 'h4'}
          gutterBottom 
          sx={{ 
            fontWeight: 700, 
            background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 1,
          }}
        >
          🏥 Health Chatbot
        </Typography>
        <Typography 
          variant={isMobile ? 'body1' : 'h6'}
          color="text.primary" 
          sx={{ mb: 2, fontWeight: 500, opacity: 0.9 }}
        >
          Your AI-powered medical assistant
        </Typography>
        <Typography 
          variant="body2" 
          color="text.primary"
          sx={{ 
            maxWidth: 600, 
            mx: 'auto',
            lineHeight: 1.6,
            fontSize: { xs: '0.875rem', sm: '1rem' },
            opacity: 0.8,
            fontWeight: 400
          }}
        >
          Ask me about health, symptoms, treatments, and wellness. I can help you understand medical information and provide guidance based on authoritative health sources.
        </Typography>
      </Box>

      {/* Features */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" color="text.primary" sx={{ mb: 1.5, fontWeight: 600, opacity: 0.9 }}>
          What I can help with:
        </Typography>
        <Box sx={{ 
          display: 'flex', 
          flexWrap: 'wrap', 
          gap: 1, 
          justifyContent: 'center',
          mb: 2
        }}>
          {features.map((feature, index) => (
            <Chip
              key={index}
              icon={feature.icon}
              label={feature.label}
              variant="outlined"
              size="small"
              color={feature.color as any}
              sx={{ 
                fontSize: '0.75rem',
                height: 28,
              }}
            />
          ))}
        </Box>
      </Box>

      {/* Example Questions */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" color="text.primary" sx={{ mb: 1.5, fontWeight: 600, opacity: 0.9 }}>
          💡 Try asking:
        </Typography>
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: 0.8,
          alignItems: 'center'
        }}>
          {exampleQuestions.slice(0, isMobile ? 3 : 5).map((question, index) => (
            <Typography
              key={index}
              variant="body2"
              color="text.primary"
              sx={{
                cursor: 'pointer',
                padding: '4px 8px',
                borderRadius: 1,
                fontSize: '0.8rem',
                opacity: 0.8,
                fontWeight: 400,
                '&:hover': {
                  backgroundColor: 'action.hover',
                  color: 'primary.main',
                  opacity: 1,
                },
                transition: 'all 0.2s ease',
              }}
            >
              ● {question}
            </Typography>
          ))}
        </Box>
      </Box>

      {/* Medical Disclaimer */}
      <Box
        sx={{
          mt: 2,
          p: 2,
          borderRadius: 2,
          backgroundColor: theme.palette.mode === 'dark' 
            ? 'rgba(255, 152, 0, 0.1)' 
            : 'rgba(255, 152, 0, 0.05)',
          border: theme.palette.mode === 'dark' 
            ? '1px solid rgba(255, 152, 0, 0.2)' 
            : '1px solid rgba(255, 152, 0, 0.1)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <WarningIcon sx={{ color: 'warning.main', fontSize: 20 }} />
          <Typography variant="subtitle2" color="warning.main" sx={{ fontWeight: 600 }}>
            Important Medical Disclaimer
          </Typography>
        </Box>
        <Typography variant="caption" color="text.primary" sx={{ fontSize: '0.75rem', lineHeight: 1.4, opacity: 0.8, fontWeight: 400 }}>
          This AI assistant provides general health information only. It is NOT a substitute for professional 
          medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for 
          medical concerns. In case of medical emergency, call emergency services immediately.
        </Typography>
        <Typography 
          variant="caption" 
          color="primary.main" 
          sx={{ 
            display: 'block', 
            mt: 1, 
            fontSize: '0.7rem',
            fontWeight: 500
          }}
        >
          ✓ Powered by advanced AI and authoritative health sources
        </Typography>
      </Box>
    </Box>
  )
}

export default WelcomeContent
