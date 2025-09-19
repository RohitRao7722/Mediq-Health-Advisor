import React from 'react'
import {
  Drawer,
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  Switch,
  Slider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Divider,
  IconButton,
  useTheme,
} from '@mui/material'
import {
  Close as CloseIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material'
import { useChatStore } from '../store/chatStore'
import { useThemeContext } from '../theme/ThemeProvider'

interface SettingsPanelProps {
  open: boolean
  onClose: () => void
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({ open, onClose }) => {
  const theme = useTheme()
  const { settings, updateSettings, resetSettings } = useChatStore()

  const handleSettingChange = (key: string, value: any) => {
    updateSettings({ [key]: value })
  }

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      sx={{
        '& .MuiDrawer-paper': {
          width: 320,
          backgroundColor: 'background.paper',
          borderLeft: 1,
          borderColor: 'divider',
        },
      }}
    >
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SettingsIcon />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Settings
            </Typography>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>

        <List>
          {/* Theme Settings */}
          <ListItem>
            <ListItemText
              primary="Theme"
              secondary="Choose your preferred theme"
            />
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <Select
                value={settings.theme}
                onChange={(e) => handleSettingChange('theme', e.target.value)}
              >
                <MenuItem value="light">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LightModeIcon fontSize="small" />
                    Light
                  </Box>
                </MenuItem>
                <MenuItem value="dark">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <DarkModeIcon fontSize="small" />
                    Dark
                  </Box>
                </MenuItem>
                <MenuItem value="auto">Auto</MenuItem>
              </Select>
            </FormControl>
          </ListItem>

          <Divider sx={{ my: 1 }} />

          {/* Font Size */}
          <ListItem>
            <ListItemText
              primary="Font Size"
              secondary="Adjust text size for better readability"
            />
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <Select
                value={settings.fontSize}
                onChange={(e) => handleSettingChange('fontSize', e.target.value)}
              >
                <MenuItem value="small">Small</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="large">Large</MenuItem>
              </Select>
            </FormControl>
          </ListItem>

          <Divider sx={{ my: 1 }} />

          {/* AI Model Settings */}
          <ListItem>
            <ListItemText
              primary="AI Model"
              secondary="Current model: llama-3.1-8b-instant"
            />
          </ListItem>

          {/* Temperature */}
          <ListItem>
            <Box sx={{ width: '100%' }}>
              <ListItemText
                primary="Response Creativity"
                secondary={`Temperature: ${settings.temperature}`}
              />
              <Slider
                value={settings.temperature}
                onChange={(_, value) => handleSettingChange('temperature', value)}
                min={0}
                max={1}
                step={0.1}
                marks={[
                  { value: 0, label: 'Focused' },
                  { value: 0.5, label: 'Balanced' },
                  { value: 1, label: 'Creative' },
                ]}
                sx={{ mt: 1 }}
              />
            </Box>
          </ListItem>

          {/* Max Tokens */}
          <ListItem>
            <Box sx={{ width: '100%' }}>
              <ListItemText
                primary="Response Length"
                secondary={`Max tokens: ${settings.maxTokens}`}
              />
              <Slider
                value={settings.maxTokens}
                onChange={(_, value) => handleSettingChange('maxTokens', value)}
                min={100}
                max={2000}
                step={100}
                marks={[
                  { value: 100, label: 'Short' },
                  { value: 1000, label: 'Medium' },
                  { value: 2000, label: 'Long' },
                ]}
                sx={{ mt: 1 }}
              />
            </Box>
          </ListItem>

          <Divider sx={{ my: 1 }} />

          {/* Display Settings */}
          <ListItem>
            <ListItemText
              primary="Show Sources"
              secondary="Display source citations with responses"
            />
            <Switch
              checked={settings.showSources}
              onChange={(e) => handleSettingChange('showSources', e.target.checked)}
            />
          </ListItem>

          <ListItem>
            <ListItemText
              primary="Streaming Responses"
              secondary="Show responses as they are generated"
            />
            <Switch
              checked={settings.enableStreaming}
              onChange={(e) => handleSettingChange('enableStreaming', e.target.checked)}
            />
          </ListItem>

          <ListItem>
            <ListItemText
              primary="Voice Input"
              secondary="Enable voice recording (coming soon)"
            />
            <Switch
              checked={settings.voiceEnabled}
              onChange={(e) => handleSettingChange('voiceEnabled', e.target.checked)}
              disabled
            />
          </ListItem>

          <Divider sx={{ my: 2 }} />

          {/* Reset Settings */}
          <ListItem>
            <ListItemText
              primary="Reset Settings"
              secondary="Restore default configuration"
            />
            <IconButton
              onClick={resetSettings}
              sx={{
                background: 'rgba(244, 67, 54, 0.1)',
                color: 'error.main',
                '&:hover': {
                  background: 'rgba(244, 67, 54, 0.2)',
                },
              }}
            >
              <CloseIcon />
            </IconButton>
          </ListItem>
        </List>

        {/* Footer */}
        <Box sx={{ mt: 'auto', pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center', display: 'block' }}>
            Settings are saved automatically
          </Typography>
        </Box>
      </Box>
    </Drawer>
  )
}

export default SettingsPanel
