# Enhanced AI Notebook System with MCP Integration

A powerful, AI-driven notebook system that uses Model Context Protocol (MCP) and multi-agent architecture to create, execute, and manage data science workflows. This system provides Cursor AI-like capabilities specifically designed for Jupyter notebook workflows.

## 🚀 Key Features

### **AI-Powered Workflow Generation**
- **Multi-Agent AI System**: 6 specialized AI agents working collaboratively
- **MCP Integration**: Model Context Protocol for powerful AI capabilities
- **Local LLM Support**: Ollama integration with Qwen2.5:3b model
- **Context-Aware Generation**: AI understands dataset structure and workflow context

### **Advanced DAG Management**
- **Dependency Tracking**: Automatic detection of code dependencies
- **Import Management**: Tracks and manages Python imports across blocks
- **Variable Flow**: Monitors variable definitions and usage
- **Execution Order**: Intelligent execution planning based on dependencies
- **Cycle Detection**: Prevents circular dependencies

### **Enhanced Python Execution**
- **Session Management**: Persistent Python sessions with variable persistence
- **Context Preservation**: Maintains state across block executions
- **Error Handling**: Comprehensive error tracking and debugging
- **Memory Management**: Efficient resource usage and cleanup
- **Timeout Protection**: Prevents infinite loops and long-running code

### **Real-Time Collaboration**
- **WebSocket Communication**: Live updates and real-time collaboration
- **Execution Monitoring**: Real-time block execution status
- **Live Output**: Instant feedback on code execution
- **Multi-User Support**: Collaborative workflow development

## 🏗️ Architecture

### **Multi-Agent AI System**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Workflow       │    │   Code          │    │   Data          │
│   Planner       │    │   Executor      │    │   Analyzer      │
│                 │    │                 │    │                 │
│ • Context       │    │ • Code Gen      │    │ • Data Insights │
│ • Optimization  │    │ • Execution     │    │ • Patterns      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Agent         │
                    │   Manager       │
                    │                 │
                    │ • Coordination  │
                    │ • Task Routing  │
                    │ • MCP Client    │
                    └─────────────────┘
```

### **DAG System**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Block 1   │───▶│   Block 2   │───▶│   Block 3   │
│ (Data Load) │    │ (Analysis)  │    │ (Viz)      │
│             │    │             │    │             │
│ Variables:  │    │ Variables:  │    │ Variables:  │
│ - df        │    │ - stats     │    │ - plot      │
│ - raw_data  │    │ - summary   │    │ - fig       │
└─────────────┘    └─────────────┘    └─────────────┘
```

### **Python Execution Engine**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Session       │    │   Code          │    │   Result        │
│   Manager       │    │   Executor      │    │   Processor     │
│                 │    │                 │    │                 │
│ • Variables     │    │ • Safe Exec     │    │ • Output Parse  │
│ • Imports       │    │ • Timeout       │    │ • Var Extract   │
│ • History       │    │ • Context       │    │ • State Update  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Installation & Setup

### **Prerequisites**
- Python 3.8+
- Ollama (for local LLM)
- Node.js 16+ (for frontend)

### **Backend Setup**

1. **Navigate to backend directory:**
   ```bash
   cd demo/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama and Qwen2.5:3b:**
   ```bash
   # Install Ollama (https://ollama.ai/)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull the model
   ollama pull qwen2.5:3b
   ```

5. **Start the enhanced backend:**
   ```bash
   python main_enhanced.py
   ```

### **Frontend Setup**

1. **Navigate to frontend directory:**
   ```bash
   cd demo/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

## 🎯 Usage Examples

### **Stock Market Momentum Strategy**

1. **Upload the stock dataset:**
   ```bash
   curl -X POST "http://localhost:8000/upload-dataset" \
        -F "file=@stock_data_sample.csv"
   ```

2. **Generate momentum strategy workflow:**
   ```bash
   curl -X POST "http://localhost:8000/ai/process" \
        -H "Content-Type: application/json" \
        -d '{
          "prompt": "Create a momentum trading strategy for this stock data. Include data loading, momentum calculation, signal generation, and backtesting with performance metrics.",
          "dataset_id": "your_dataset_id"
        }'
   ```

3. **The AI will generate blocks for:**
   - Data loading and preprocessing
   - Momentum indicator calculation
   - Trading signal generation
   - Backtesting framework
   - Performance analysis and visualization

### **Custom AI Prompts**

- **"Analyze this dataset and create a comprehensive EDA workflow"**
- **"Build a machine learning pipeline for classification"**
- **"Create interactive visualizations for time series analysis"**
- **"Implement a custom trading strategy with risk management"**

## 🔧 API Endpoints

### **Core Endpoints**
- `POST /upload-dataset` - Upload CSV dataset
- `GET /datasets` - Get all datasets
- `POST /ai/process` - Process AI request and generate workflow
- `GET /workflows` - Get all workflows
- `GET /workflows/{id}` - Get workflow details

### **AI System Endpoints**
- `GET /ai/agents` - Get AI agent information
- `GET /ai/agents/{id}/execute` - Execute task with specific agent
- `GET /dag/status` - Get DAG system status
- `GET /executor/status` - Get Python executor status

### **Block Management**
- `POST /blocks` - Create new block
- `PUT /blocks/{id}` - Update block
- `DELETE /blocks/{id}` - Delete block
- `POST /blocks/{id}/execute` - Execute single block
- `POST /workflows/{id}/execute` - Execute entire workflow

### **Real-Time Communication**
- `WS /ws/workflow/{id}` - WebSocket for workflow updates

## 🤖 AI Agents

### **1. Workflow Planner (planner_001)**
- **Capabilities**: Context understanding, workflow optimization
- **Role**: Plans overall workflow structure and optimization
- **Model**: Qwen2.5:3b

### **2. Code Executor (executor_001)**
- **Capabilities**: Code generation, code execution
- **Role**: Generates and executes Python code
- **Model**: Qwen2.5:3b

### **3. Data Analyzer (analyzer_001)**
- **Capabilities**: Data analysis, context understanding
- **Role**: Analyzes data and provides insights
- **Model**: Qwen2.5:3b

### **4. Data Visualizer (visualizer_001)**
- **Capabilities**: Visualization, code generation
- **Role**: Creates charts and plots
- **Model**: Qwen2.5:3b

### **5. Code Debugger (debugger_001)**
- **Capabilities**: Error diagnosis, code generation
- **Role**: Fixes code errors and issues
- **Model**: Qwen2.5:3b

### **6. Workflow Optimizer (optimizer_001)**
- **Capabilities**: Workflow optimization, context understanding
- **Role**: Optimizes workflow performance
- **Model**: Qwen2.5:3b

## 📊 DAG Features

### **Dependency Types**
- **Data Flow**: Variables passed between blocks
- **Import Dependency**: Required imports
- **Function Dependency**: Function calls between blocks
- **Execution Order**: Position-based dependencies
- **Variable Dependency**: Variable usage tracking

### **Code Analysis**
- **AST Parsing**: Python Abstract Syntax Tree analysis
- **Import Detection**: Automatic import tracking
- **Variable Tracking**: Variable definition and usage
- **Function Analysis**: Function definitions and calls
- **Complexity Estimation**: Code complexity metrics

### **Validation**
- **Cycle Detection**: Prevents circular dependencies
- **Dependency Validation**: Ensures valid block relationships
- **Execution Plan**: Optimized execution order
- **Error Detection**: Identifies potential issues

## 🔄 Python Execution Features

### **Session Management**
- **Persistent Variables**: Variables persist across executions
- **Import History**: Tracks all imports
- **Execution History**: Complete execution log
- **Memory Management**: Efficient resource usage

### **Safety Features**
- **Timeout Protection**: Prevents infinite loops
- **Output Limits**: Prevents memory overflow
- **Error Isolation**: Isolates execution errors
- **Context Preservation**: Maintains execution state

### **Context Injection**
- **Dataset Context**: Automatic dataset variable injection
- **Session Variables**: Previous execution results
- **Global Imports**: Common data science libraries
- **Custom Context**: User-defined context variables

## 🌐 Real-Time Features

### **WebSocket Communication**
- **Live Updates**: Real-time execution status
- **Block Execution**: Live block execution monitoring
- **Error Broadcasting**: Instant error notifications
- **System Metrics**: Live system performance data

### **Collaboration Features**
- **Multi-User Support**: Multiple users can work simultaneously
- **Real-Time Editing**: Live collaboration on workflows
- **Execution Monitoring**: Watch others execute code
- **Instant Feedback**: Immediate response to changes

## 📈 Performance & Scalability

### **Optimization Features**
- **Lazy Loading**: Load only required components
- **Session Cleanup**: Automatic cleanup of inactive sessions
- **Memory Management**: Efficient memory usage
- **Connection Pooling**: Optimized database connections

### **Monitoring & Metrics**
- **Execution Time**: Track block execution performance
- **Memory Usage**: Monitor resource consumption
- **Error Rates**: Track execution success rates
- **System Health**: Overall system performance metrics

## 🔒 Security Features

### **Code Execution Safety**
- **Sandboxed Execution**: Isolated execution environment
- **Timeout Limits**: Prevents resource abuse
- **Output Sanitization**: Safe output handling
- **Error Isolation**: Prevents system crashes

### **Data Security**
- **File Upload Validation**: Secure file handling
- **Session Isolation**: User session separation
- **Access Control**: Workflow access management
- **Audit Logging**: Complete activity logging

## 🧪 Testing & Development

### **Testing the System**

1. **Start the backend:**
   ```bash
   cd demo/backend
   python main_enhanced.py
   ```

2. **Test AI capabilities:**
   ```bash
   # Test agent system
   curl "http://localhost:8000/ai/agents"
   
   # Test system status
   curl "http://localhost:8000/system/status"
   ```

3. **Test workflow creation:**
   ```bash
   # Upload sample data
   curl -X POST "http://localhost:8000/upload-dataset" \
        -F "file=@stock_data_sample.csv"
   
   # Create AI workflow
   curl -X POST "http://localhost:8000/ai/process" \
        -H "Content-Type: application/json" \
        -d '{"prompt": "Analyze this stock data", "dataset_id": "your_id"}'
   ```

### **Development Workflow**

1. **Modify AI agents** in `mcp_system.py`
2. **Update DAG logic** in `dag_system.py`
3. **Enhance execution** in `python_executor.py`
4. **Test changes** with the sample dataset
5. **Monitor logs** for debugging information

## 🚀 Production Deployment

### **Environment Variables**
```bash
export OLLAMA_HOST=http://localhost:11434
export MCP_SERVER_URL=your_mcp_server_url
export DATABASE_URL=your_database_url
export REDIS_URL=your_redis_url
```

### **Docker Deployment**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main_enhanced.py"]
```

### **Scaling Considerations**
- **Load Balancing**: Multiple backend instances
- **Database**: Persistent storage for workflows
- **Caching**: Redis for session management
- **Monitoring**: Prometheus + Grafana
- **Logging**: Centralized logging system

## 🤝 Contributing

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### **Code Style**
- Follow PEP 8 for Python code
- Use type hints
- Add comprehensive docstrings
- Include error handling
- Write unit tests

## 📚 Resources

### **Documentation**
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Ollama Documentation](https://ollama.ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [NetworkX Documentation](https://networkx.org/)

### **Related Projects**
- [Cursor AI](https://cursor.sh/)
- [Jupyter Notebook](https://jupyter.org/)
- [VS Code](https://code.visualstudio.com/)
- [Streamlit](https://streamlit.io/)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **MCP Community** for the Model Context Protocol
- **Ollama Team** for local LLM capabilities
- **FastAPI Team** for the excellent web framework
- **OpenAI** for inspiration in AI-powered development tools

---

**Ready to build the future of AI-powered data science?** 🚀

Start with the enhanced backend and create powerful, intelligent workflows that understand your data and adapt to your needs!
