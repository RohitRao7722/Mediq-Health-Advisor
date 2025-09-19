import React, { createContext, useContext, useMemo } from 'react'
import { ThemeProvider as MuiThemeProvider, createTheme } from '@mui/material/styles'
import { useChatStore } from '../store/chatStore'

interface ThemeContextType {
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export const useThemeContext = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useThemeContext must be used within a ThemeProvider')
  }
  return context
}

interface CustomThemeProviderProps {
  children: React.ReactNode
}

export const CustomThemeProvider: React.FC<CustomThemeProviderProps> = ({ children }) => {
  const { settings, updateSettings } = useChatStore()

  const toggleTheme = () => {
    const newTheme = settings.theme === 'light' ? 'dark' : 'light'
    updateSettings({ theme: newTheme })
  }

  const theme = useMemo(() => {
    const isDark = settings.theme === 'dark' || 
      (settings.theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches)

    return createTheme({
      palette: {
        mode: isDark ? 'dark' : 'light',
        primary: {
          main: '#1976d2',
          light: '#42a5f5',
          dark: '#1565c0',
        },
        secondary: {
          main: '#dc004e',
        },
        background: {
          default: isDark ? '#0a0a0a' : '#f5f5f5',
          paper: isDark ? '#1a1a1a' : '#ffffff',
        },
        text: {
          primary: isDark ? '#ffffff' : '#1a1a1a',
          secondary: isDark ? '#e0e0e0' : '#424242',
        },
        divider: isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.12)',
        action: {
          hover: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.04)',
          selected: isDark ? 'rgba(255,255,255,0.16)' : 'rgba(0,0,0,0.08)',
        },
      },
      typography: {
        fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
        h1: {
          fontWeight: 600,
        },
        h2: {
          fontWeight: 600,
        },
        h3: {
          fontWeight: 600,
        },
        h4: {
          fontWeight: 600,
        },
        h5: {
          fontWeight: 600,
        },
        h6: {
          fontWeight: 600,
        },
      },
      shape: {
        borderRadius: 12,
      },
      components: {
        MuiButton: {
          styleOverrides: {
            root: {
              textTransform: 'none',
              fontWeight: 500,
            },
          },
        },
        MuiCard: {
          styleOverrides: {
            root: {
              boxShadow: isDark 
                ? '0 2px 8px rgba(0,0,0,0.3)' 
                : '0 2px 8px rgba(0,0,0,0.1)',
            },
          },
        },
        MuiPaper: {
          styleOverrides: {
            root: {
              backgroundImage: 'none',
            },
          },
        },
      },
    })
  }, [settings.theme])

  return (
    <ThemeContext.Provider value={{ toggleTheme }}>
      <MuiThemeProvider theme={theme}>
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  )
}

