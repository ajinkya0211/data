# 🚀 AI Notebook System - Frontend

A beautiful, powerful, and intuitive frontend for the AI Notebook System built with Next.js, TypeScript, and shadcn/ui components.

## ✨ Features

### 🎨 **Modern Design System**
- **shadcn/ui Components**: Beautiful, accessible, and customizable UI components
- **Tailwind CSS**: Utility-first CSS framework for rapid development
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Apple-Inspired UI**: Clean, simple, and powerful user experience

### 🤖 **AI Integration**
- **Multi-AI Provider Support**: Ollama (local), OpenAI, Gemini
- **Natural Language to Code**: AI-powered code generation
- **Context-Aware Assistance**: AI understands your project state
- **Real-time AI Chat**: Interactive AI assistance sidebar

### 📊 **Data Science Workspace**
- **Notebook View**: Traditional cell-based interface like Jupyter
- **DAG Workflow View**: Visual workflow editor with ReactFlow
- **Data Explorer**: Dataset management and profiling
- **Live Execution**: Real-time code execution monitoring

### 🔄 **Real-time Features**
- **WebSocket Integration**: Live updates and collaboration
- **Execution Monitoring**: Real-time status and progress tracking
- **Live Collaboration**: Team collaboration and shared sessions

## 🛠️ Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Charts**: Recharts
- **Code Editor**: Monaco Editor (ready for integration)
- **Workflow**: ReactFlow (ready for integration)

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Run the development server**
```bash
npm run dev
```

4. **Open your browser**
Navigate to [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── page.tsx           # Landing page
│   │   ├── auth/              # Authentication pages
│   │   ├── dashboard/         # Dashboard page
│   │   ├── project/[id]/      # Project workspace
│   │   └── demo/              # Interactive demo
│   ├── components/            # Reusable components
│   │   └── ui/               # shadcn/ui components
│   └── lib/                  # Utility functions
├── public/                   # Static assets
├── tailwind.config.js        # Tailwind configuration
├── components.json           # shadcn/ui configuration
└── package.json             # Dependencies
```

## 🎯 Pages & Features

### 🏠 **Landing Page** (`/`)
- Hero section with value proposition
- Feature highlights and capabilities
- Call-to-action buttons
- Professional design with animations

### 🔐 **Authentication** (`/auth`)
- Login and registration forms
- OAuth integration ready
- Form validation and error handling
- Responsive design for all devices

### 📊 **Dashboard** (`/dashboard`)
- Project overview and management
- Quick actions (New Project, Import Data, AI Chat)
- Recent activity and statistics
- AI provider status monitoring

### 💻 **Project Workspace** (`/project/[id]`)
- **Notebook View**: Cell-based code editing
- **DAG View**: Visual workflow editor
- **AI Sidebar**: Context-aware AI assistance
- **Data Explorer**: Dataset management
- **Execution Control**: Run, stop, and monitor code

### 🎭 **Interactive Demo** (`/demo`)
- Feature demonstrations
- Interactive examples
- AI code generation showcase
- Workflow visualization

## 🎨 Design System

### **Color Palette**
- **Primary**: Blue (#2563eb) to Indigo (#4f46e5)
- **Success**: Green (#16a34a)
- **Warning**: Yellow (#ca8a04)
- **Error**: Red (#dc2626)
- **Neutral**: Gray scale (#f8fafc to #0f172a)

### **Typography**
- **Font**: Inter (Google Fonts)
- **Headings**: Bold, large, clear hierarchy
- **Body**: Readable, comfortable line height
- **Code**: Monospace for code blocks

### **Components**
- **Cards**: Clean, elevated design with shadows
- **Buttons**: Multiple variants (primary, secondary, outline, ghost)
- **Forms**: Accessible inputs with proper labels
- **Navigation**: Clear, intuitive navigation patterns

## 🔧 Configuration

### **Tailwind CSS**
The project uses Tailwind CSS v4 with custom configuration for:
- Color schemes
- Typography scales
- Spacing and layout
- Component variants

### **shadcn/ui**
Components are configured through `components.json`:
- Base color: Zinc
- CSS variables for theming
- Component customization
- TypeScript support

### **Environment Variables**
Create a `.env.local` file for:
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# AI Provider Keys (for production)
NEXT_PUBLIC_OPENAI_API_KEY=your_key_here
NEXT_PUBLIC_GEMINI_API_KEY=your_key_here
```

## 🚀 Development

### **Available Scripts**
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript check
```

### **Adding New Components**
1. Use shadcn/ui CLI:
```bash
npx shadcn@latest add [component-name]
```

2. Or create custom components in `src/components/`

### **Styling Guidelines**
- Use Tailwind utility classes
- Follow the established design system
- Maintain consistency across components
- Ensure accessibility standards

## 📱 Responsive Design

### **Breakpoints**
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

### **Mobile-First Approach**
- Start with mobile layouts
- Progressive enhancement for larger screens
- Touch-friendly interactions
- Optimized for mobile performance

## ♿ Accessibility

### **Standards Compliance**
- WCAG 2.1 AA compliance
- Semantic HTML structure
- Proper ARIA labels
- Keyboard navigation support

### **Features**
- Screen reader compatibility
- High contrast mode support
- Focus management
- Color contrast compliance

## 🔒 Security

### **Frontend Security**
- Input validation and sanitization
- XSS protection
- CSRF token handling
- Secure authentication flows

### **Data Protection**
- No sensitive data in client-side code
- Secure API communication
- Environment variable protection
- HTTPS enforcement

## 🧪 Testing

### **Testing Strategy**
- Component testing with Jest
- E2E testing with Playwright
- Accessibility testing
- Cross-browser compatibility

### **Running Tests**
```bash
npm run test         # Run unit tests
npm run test:e2e     # Run E2E tests
npm run test:a11y    # Run accessibility tests
```

## 📦 Deployment

### **Build Process**
```bash
npm run build        # Create production build
npm run start        # Start production server
```

### **Deployment Options**
- **Vercel**: Optimized for Next.js
- **Netlify**: Static site generation
- **AWS**: Custom deployment
- **Docker**: Containerized deployment

### **Environment Setup**
1. Set production environment variables
2. Configure API endpoints
3. Set up monitoring and analytics
4. Configure CDN and caching

## 🤝 Contributing

### **Development Workflow**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### **Code Standards**
- Follow TypeScript best practices
- Use ESLint and Prettier
- Write meaningful commit messages
- Document new features

## 📚 Documentation

### **Additional Resources**
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

### **API Integration**
- Backend API documentation
- WebSocket implementation guide
- Authentication flow documentation
- Error handling patterns

## 🐛 Troubleshooting

### **Common Issues**

**Build Errors**
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

**Dependency Issues**
```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Styling Issues**
```bash
# Rebuild Tailwind CSS
npm run build:css
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Community**: Join our community channels

---

## 🎉 **Ready to Build the Future of Data Science?**

The AI Notebook System frontend provides a powerful, beautiful, and intuitive interface for modern data science workflows. With AI assistance, visual workflows, and real-time collaboration, you can focus on what matters most - your data and insights.

**🚀 Start building today!**
