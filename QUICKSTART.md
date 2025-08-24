# 🚀 AI Notebook System - Quick Start Guide

Get your AI-integrated smart Python notebook system up and running in minutes!

## 🎯 What You'll Get

- **AI-Powered Workflows**: Natural language to code blocks
- **Visual DAG Editor**: Drag-and-drop workflow builder
- **Smart Data Profiling**: Automatic dataset understanding
- **Real-time Execution**: Live code execution with Jupyter kernels
- **Professional UI**: Modern, responsive interface

## ⚡ Quick Start (5 minutes)

### 1. Prerequisites

- **Docker & Docker Compose** - [Install here](https://docs.docker.com/get-docker/)
- **Python 3.11+** - [Install here](https://www.python.org/downloads/)
- **Node.js 18+** - [Install here](https://nodejs.org/)

### 2. Clone & Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-notebook-system

# Run the automated setup script
./setup.sh
```

The setup script will:
- ✅ Check prerequisites
- ✅ Create environment files
- ✅ Install dependencies
- ✅ Start all services
- ✅ Show access URLs

### 3. Access Your System

After setup completes, access:

- **🎨 Frontend**: http://localhost:3000
- **🔧 API**: http://localhost:8000
- **📚 API Docs**: http://localhost:8000/docs
- **💾 MinIO Console**: http://localhost:9001

## 🎮 Your First Workflow

### 1. Create a Project
- Open http://localhost:3000
- Click "New Project"
- Name it "Sales Analysis"

### 2. Upload Your Data
- Use the sample `data_dirty.csv` in the `data/` folder
- Click "Upload Dataset"
- Watch automatic profiling happen!

### 3. Ask AI to Build
- Type in chat: *"Load the sales data and show me total sales by category"*
- AI creates blocks automatically
- See the visual DAG build in real-time

### 4. Execute & View Results
- Click "Run All"
- Watch live execution
- See charts, tables, and outputs

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │  Jupyter Kernel │
│   (Port 3000)   │◄──►│   (Port 8000)   │◄──►│   (Port 8888)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   (Port 5432)   │
                    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │ Redis + MinIO   │
                    │ (Ports 6379,9000)│
                    └─────────────────┘
```

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Database Setup
```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis minio

# Wait for services to be ready, then start backend
```

## 🌟 Key Features to Try

### AI Chat Integration
- Ask: *"Create a bar chart of sales by category"*
- AI generates Python code automatically
- See real-time block creation

### Visual DAG Editor
- Drag blocks to reposition
- Connect blocks with edges
- Right-click for context menus

### Data Profiling
- Upload any CSV/Parquet file
- Automatic schema detection
- Statistical summaries

### Real-time Execution
- Live output streaming
- Error handling with AI suggestions
- Execution history

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Check what's using the port
lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

**Database connection failed:**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres
```

**Frontend not loading:**
```bash
# Check if Node modules are installed
cd frontend && npm install

# Check for build errors
npm run build
```

### Reset Everything
```bash
# Stop all services
docker-compose down

# Remove volumes (⚠️ deletes all data)
docker-compose down -v

# Restart fresh
./setup.sh
```

## 📚 Next Steps

### For Developers
- Explore the codebase structure
- Add new block types
- Extend AI capabilities
- Customize the UI

### For Users
- Import your own datasets
- Build complex workflows
- Export to notebooks/PDFs
- Share projects with team

### For Production
- Set up proper authentication
- Configure SSL certificates
- Set up monitoring
- Scale with Kubernetes

## 🆘 Need Help?

- **Documentation**: Check `/docs` folder
- **Issues**: Create GitHub issue
- **Community**: Join our discussions
- **Support**: Contact the team

## 🎉 You're Ready!

Your AI Notebook System is now running! Start building amazing data workflows with the power of AI.

**Happy coding! 🚀** 