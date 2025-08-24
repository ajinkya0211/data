# 🔹 AI-Integrated Smart Python Notebook System

A deep AI integrated smart Python notebook system with a slick UI that combines the power of Jupyter notebooks with AI assistance, visual DAG workflows, and professional data science tooling.

## 🚀 **NEW: Multi-AI Provider Support!**

**Default: Ollama (Local)** - Run AI models locally for privacy and speed
**Plus: OpenAI & Gemini** - Cloud AI when you need more power

- 🤖 **Ollama (Local)**: Fast, private, no API costs
- 🌐 **OpenAI GPT-4**: Enterprise-grade AI capabilities  
- 🔮 **Google Gemini**: Advanced reasoning and analysis
- 🔄 **Automatic Fallback**: Seamless provider switching

## 🏗️ Architecture Overview

```
[ Web App (React) ]
     │  ├─ REST/WS
     ▼
[API Gateway (FastAPI)] ──────────────────────────────────────────────────────────┐
     │                                                                           │
     ├── Project/Parser Service  ──┐                                             │
     │     (blocks+DAG+versions)   │  emits events   ┌─> [Redis/Queue] ──> Executor
     │                             │─────────────────┘                           │
     ├── Data Catalog Service  <───┤  profiles/update                             │
     │     (datasets+profiles)     │                                             │
     ├── Execution Service (Kernels+Scheduler+Artifacts) ◀─────┐                │
     │     (jupyter_client / kernels)                           │ WS events     │
     ├── LLM Orchestrator (Multi-Provider) ◀────────────────────┘                │
     │     (Ollama + OpenAI + Gemini)                                           │
     ├── Auth/RBAC Service                                                        │
     │                                                                           │
     ├── Realtime/Event Hub  (WebSocket)                                          │
     │                                                                           │
     ├── Postgres (metadata)     ──> versioned state                              │
     ├── S3/MinIO (artifacts)    ──> outputs, html, images, parquet               │
     └── Redis (cache/queue)     ──> runs, plans, locks                           
```

## 🚀 Features

- **🤖 Multi-AI Provider Support**: Ollama (local), OpenAI, Gemini
- **AI-Powered Workflows**: Natural language to code blocks via LLM orchestration
- **Visual DAG Editor**: ReactFlow-based canvas for building data pipelines
- **Smart Data Profiling**: Automatic dataset understanding and metadata extraction
- **Incremental Execution**: Only run affected blocks when dependencies change
- **Real-time Collaboration**: WebSocket-based live updates and collaboration
- **Professional Export**: Notebook, script, and report generation
- **Version Control**: Complete project history with diff views

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Primary database for metadata
- **Redis**: Caching, queues, and WebSocket pub/sub
- **Jupyter Client**: Python kernel execution
- **Pydantic**: Data validation and serialization
- **Celery**: Background task processing

### AI & ML Providers
- **Ollama**: Local AI models (llama3.2, codellama, mistral)
- **OpenAI**: GPT-4 and GPT-3.5 models
- **Google Gemini**: Advanced reasoning models
- **LangChain**: AI agent framework integration

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **ReactFlow**: DAG visualization and editing
- **Monaco Editor**: Code editing with language support
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Server state management

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+

### Development Setup

1. **Clone and setup**
```bash
git clone <repository>
cd ai-notebook-system

# Run the automated setup script
./setup.sh
```

2. **Access your system**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Ollama API: http://localhost:11434

## 🤖 AI Provider Configuration

### Ollama (Default - Local)
```bash
# Ollama runs locally with Docker
# Default model: llama3.2:3b
# Available models: llama3.2, codellama, mistral, neural-chat

# Download additional models
ollama pull codellama:7b
ollama pull mistral:7b

# Check available models
curl http://localhost:11434/api/tags
```

### OpenAI
```bash
# Add to .env file
OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_AI_PROVIDER=openai  # Optional: change default
```

### Google Gemini
```bash
# Add to .env file
GEMINI_API_KEY=your_gemini_api_key_here
DEFAULT_AI_PROVIDER=gemini  # Optional: change default
```

### Provider Switching
```python
# In your AI requests, specify provider
response = await ai_provider_service.generate_response(
    prompt="Your prompt here",
    provider=AIProvider.OPENAI  # or OLLAMA, GEMINI
)
```

## 📊 Sample Workflow

1. **Create Project**: Start a new "Sales Analysis" project
2. **Import Data**: Upload `data_dirty.csv` - automatic profiling
3. **AI Chat**: "Show me total sales by category with a bar chart"
4. **AI Response**: Uses Ollama (local) by default, or specify provider
5. **Visual DAG**: See the generated blocks and their dependencies
6. **Execute**: Run the pipeline and view results
7. **Export**: Generate notebook or report

## 🔧 Configuration

### Environment Variables
```bash
# AI Provider Configuration
DEFAULT_AI_PROVIDER=ollama  # ollama, openai, gemini

# Ollama (Local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2:3b

# OpenAI
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4.1-mini

# Gemini
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-1.5-pro

# Other services
DATABASE_URL=postgresql://user:pass@localhost/notebooks
REDIS_URL=redis://localhost:6379
JWT_SECRET=your_jwt_secret
```

## 🌟 AI Features

### Code Generation
- Natural language to Python code
- Data science specific prompts
- Error analysis and fixes
- Code explanation and optimization

### Workflow Assistance
- DAG optimization suggestions
- Performance recommendations
- Best practices guidance
- Alternative approach suggestions

### Multi-Provider Benefits
- **Ollama**: Fast, private, no API costs
- **OpenAI**: High-quality, enterprise features
- **Gemini**: Advanced reasoning, cost-effective
- **Fallback**: Automatic provider switching

## 📈 Roadmap

### Phase 1: POC (Current)
- [x] Multi-AI provider support
- [x] Ollama local integration
- [x] OpenAI and Gemini support
- [x] Basic FastAPI backend
- [x] React frontend with DAG canvas
- [x] Data profiling service
- [ ] LLM orchestration
- [ ] Execution service

### Phase 2: MVP
- [ ] Advanced AI workflows
- [ ] Model fine-tuning
- [ ] Custom prompt templates
- [ ] AI performance analytics

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# AI provider tests
curl http://localhost:8000/api/v1/ai/health
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- Create an issue for bugs or feature requests
- Check the documentation in `/docs`
- Join our community discussions

---

⚡ **Ready to build the future of AI-powered data science? Your multi-provider AI notebook system is ready! 🚀** 