# 🏥 Health Chatbot Frontend

A modern, feature-rich React frontend for the Health Chatbot RAG system, built with Material-UI and TypeScript.

## ✨ Features

### 🎯 Essential Functionalities
- **Persistent Chat History**: Scroll through previous conversations with timestamps
- **Streaming Responses**: Real-time response generation with typing indicators
- **Source Citations**: Clear references to documents and sources used for answers
- **Context/Chunk Preview**: View actual retrieved text from knowledge base
- **Markdown & Code Highlighting**: Rich text rendering with syntax highlighting
- **Search & Navigation**: Filter and search through chat history
- **User Feedback & Rating**: Thumbs up/down and feedback system
- **Multiturn Chat**: Context-aware conversations with session management
- **Accessibility**: Full keyboard navigation and screen reader support
- **Mobile Responsive**: Optimized for desktop and mobile devices
- **Loading Indicators**: Clear progress indicators and error handling
- **Settings Panel**: Customizable model parameters and UI preferences

### 🎨 Modern UI/UX Design
- **Clean Conversation Bubbles**: Modern chat interface with avatars
- **Sticky Input**: Always-visible prompt input at bottom
- **Light/Dark Mode**: Theme switching with system preference detection
- **Collapsible Sources**: Expandable source cards in response bubbles
- **Left Sidebar**: Chat history, settings, and navigation
- **Smooth Animations**: Framer Motion animations for interactions
- **Professional Design**: Medical-grade UI with accessibility focus

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+ with RAG system set up
- Groq API key

### Installation

1. **Install Dependencies**
```bash
# Install Python dependencies
pip install flask flask-cors

# Install frontend dependencies
cd frontend
npm install
```

2. **Set Environment Variables**
```bash
export GROQ_API_KEY='your-groq-api-key-here'
```

3. **Start the Application**
```bash
# Option 1: Use the startup script
python start_frontend.py

# Option 2: Start manually
# Terminal 1: Start backend
python src/enhanced_web_chatbot.py

# Terminal 2: Start frontend
cd frontend
npm run dev
```

4. **Open in Browser**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # React components
│   │   ├── ChatInterface.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── MessageList.tsx
│   │   ├── MarkdownRenderer.tsx
│   │   ├── SourceCitations.tsx
│   │   ├── Sidebar.tsx
│   │   ├── SettingsPanel.tsx
│   │   └── ...
│   ├── store/             # State management
│   │   └── chatStore.ts
│   ├── services/          # API services
│   │   └── api.ts
│   ├── types/             # TypeScript types
│   │   └── api.ts
│   ├── App.tsx            # Main app component
│   └── main.tsx           # Entry point
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## 🎛️ Components Overview

### Core Components

#### `ChatInterface`
- Main chat interface with input handling
- Voice recording support (coming soon)
- File upload functionality
- Real-time message sending

#### `MessageBubble`
- Individual message display
- User/assistant message styling
- Source citations and metadata
- Rating and feedback system
- Copy, regenerate, delete actions

#### `MarkdownRenderer`
- Rich text rendering with markdown support
- Code syntax highlighting
- Math equation rendering (KaTeX)
- Table and list formatting
- Link handling

#### `SourceCitations`
- Expandable source cards
- Relevance scoring display
- Content preview functionality
- Metadata information
- Copy and open actions

#### `Sidebar`
- Chat history management
- Session creation and deletion
- Navigation between conversations
- Search and filter options

#### `SettingsPanel`
- Model parameter configuration
- Theme and appearance settings
- Response length and creativity controls
- Feature toggles

## 🔧 Configuration

### Environment Variables
```bash
GROQ_API_KEY=your-groq-api-key-here
```

### Settings Options
- **Theme**: Light, Dark, Auto
- **Font Size**: Small, Medium, Large
- **Temperature**: 0.0 - 1.0 (response creativity)
- **Max Tokens**: 100 - 2000 (response length)
- **Show Sources**: Toggle source citations
- **Streaming**: Enable/disable streaming responses
- **Voice Input**: Voice recording (coming soon)

## 📱 Mobile Support

The frontend is fully responsive and optimized for mobile devices:
- Touch-friendly interface
- Swipe gestures for navigation
- Optimized input handling
- Responsive message bubbles
- Mobile-specific layouts

## ♿ Accessibility Features

- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: ARIA labels and descriptions
- **High Contrast**: Support for high contrast modes
- **Focus Management**: Clear focus indicators
- **Semantic HTML**: Proper heading structure
- **Alt Text**: Image descriptions and icons

## 🎨 Theming

### Light Mode
- Clean white background
- Blue accent colors
- High contrast text
- Subtle shadows and borders

### Dark Mode
- Dark background with gradients
- Blue accent colors
- Optimized text contrast
- Reduced eye strain

### Auto Mode
- Automatically switches based on system preference
- Respects user's OS theme setting

## 🔌 API Integration

### Backend Endpoints
- `GET /api/health` - Health check
- `GET /api/info` - System information
- `POST /api/chat` - Send message
- `POST /api/chat/stream` - Streaming responses
- `POST /api/feedback` - User feedback

### Error Handling
- Network error recovery
- Graceful degradation
- User-friendly error messages
- Retry mechanisms

## 🚀 Performance Features

### Optimization
- **Code Splitting**: Lazy loading of components
- **Memoization**: React.memo for expensive components
- **Virtual Scrolling**: Efficient message list rendering
- **Debounced Input**: Optimized search and input handling
- **Caching**: API response caching with React Query

### Loading States
- Skeleton screens for content loading
- Progress indicators for long operations
- Smooth transitions and animations
- Optimistic UI updates

## 🧪 Testing

### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Testing Features
- Component testing with React Testing Library
- API mocking for development
- Error boundary testing
- Accessibility testing

## 🔒 Security Features

### Data Protection
- No sensitive data stored in frontend
- Secure API communication
- Input sanitization
- XSS protection

### Privacy
- Local storage for user preferences only
- No tracking or analytics
- GDPR compliant data handling
- Clear privacy notices

## 🐛 Troubleshooting

### Common Issues

1. **Frontend won't start**
   ```bash
   # Clear node modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Backend connection failed**
   - Check if backend is running on port 5000
   - Verify GROQ_API_KEY is set
   - Check network connectivity

3. **Build errors**
   ```bash
   # Clear build cache
   npm run build -- --force
   ```

4. **TypeScript errors**
   ```bash
   # Check TypeScript configuration
   npx tsc --noEmit
   ```

### Debug Mode
```bash
# Enable debug logging
DEBUG=true npm run dev
```

## 🚀 Deployment

### Production Build
```bash
npm run build
```

### Environment Setup
```bash
# Production environment variables
NODE_ENV=production
REACT_APP_API_URL=https://your-api-domain.com
```

### Docker Support
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🔮 Future Enhancements

- [ ] Voice input and output
- [ ] File upload and analysis
- [ ] Advanced search and filtering
- [ ] User authentication
- [ ] Conversation sharing
- [ ] Multi-language support
- [ ] Offline mode
- [ ] PWA capabilities
- [ ] Real-time collaboration
- [ ] Advanced analytics

## 📄 License

This project is for educational and research purposes. Please ensure compliance with medical data usage regulations in your jurisdiction.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the console logs
3. Ensure all dependencies are installed
4. Verify API connectivity

---

**Remember**: This is an AI assistant for general health information only. Always consult qualified healthcare professionals for medical advice, diagnosis, or treatment.

