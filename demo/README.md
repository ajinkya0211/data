# AI Notebook Demo

A simplified, presentation-ready version of the AI Notebook System that showcases the core capabilities without the complexity of authentication, database storage, and other production features.

## Features

- **AI-Powered Workflow Generation**: Upload a CSV dataset and ask the AI to create analysis workflows
- **Real-time Notebook Interface**: View and execute code blocks with live output
- **DAG Visualization**: Toggle between notebook and DAG views using ReactFlow
- **In-Memory Storage**: Everything is stored in memory for demo purposes
- **CSV Dataset Support**: Upload and analyze CSV files
- **Block Execution**: Execute individual blocks or entire workflows

## Demo Flow

1. **Upload Dataset**: Upload a CSV file through the AI sidebar
2. **AI Interaction**: Ask the AI what you want to do with the data
3. **Workflow Generation**: AI creates code blocks and workflows based on your prompt
4. **Execution**: Execute blocks individually or run the entire workflow
5. **View Modes**: Switch between notebook view (code blocks) and DAG view (visual workflow)

## Quick Start

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd demo/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   python main.py
   ```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd demo/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will run on `http://localhost:3000`

## API Endpoints

- `POST /upload-dataset` - Upload CSV dataset
- `GET /datasets` - Get all uploaded datasets
- `POST /ai/process` - Process AI request and generate workflow
- `GET /workflows/{id}` - Get workflow by ID
- `POST /blocks/{id}/execute` - Execute individual block
- `POST /workflows/{id}/execute` - Execute entire workflow

## Demo Scenarios

### Data Analysis
- Upload a CSV dataset
- Prompt: "Analyze the dataset and show basic statistics"
- AI generates blocks for data exploration, statistics, and missing value analysis

### Data Visualization
- Prompt: "Create visualizations for the data"
- AI generates plotting blocks with matplotlib/seaborn

### Data Cleaning
- Prompt: "Clean and preprocess the data"
- AI generates blocks for handling duplicates, missing values, and data transformation

## Architecture

- **Backend**: FastAPI with in-memory storage
- **Frontend**: Next.js with ReactFlow for DAG visualization
- **AI Simulation**: Mock AI responses based on prompt keywords
- **Real-time Updates**: Live execution status and output display

## Customization

To modify the AI responses, edit the `process_ai_request` function in `demo/backend/main.py`. You can:

- Add more prompt keywords
- Generate different types of blocks
- Modify block content and positioning
- Add more sophisticated AI logic

## Production Considerations

This demo is designed for presentation purposes. For production use, consider:

- Database persistence instead of in-memory storage
- Real AI integration (OpenAI, Anthropic, etc.)
- Authentication and user management
- Error handling and validation
- Scalability and performance optimization
- Security measures

## Troubleshooting

- **Backend won't start**: Check if port 8000 is available
- **Frontend won't start**: Check if port 3000 is available
- **CORS errors**: Ensure backend is running and CORS is properly configured
- **File upload issues**: Check file size and format (CSV only)

## License

This demo is part of the AI Notebook System project.
