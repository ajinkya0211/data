from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
import io
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import asyncio
import subprocess
import tempfile
import os
import sys
from pathlib import Path
import ollama
import re
from dataclasses import dataclass, asdict
from enum import Enum
import csv

# Use lifespan context manager instead of deprecated on_event
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI"""
    # Startup
    print("🚀 Starting AI Notebook Demo Backend...")
    task = asyncio.create_task(broadcast_system_metrics())
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AI Notebook Demo Backend...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

# Update FastAPI app with lifespan
app = FastAPI(
    title="AI Notebook Demo", 
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
datasets = {}
blocks = {}
workflows = {}
execution_results = {}
python_sessions = {}

class Block:
    def __init__(self, block_type: str, content: str, position: Dict[str, int]):
        self.id = str(uuid.uuid4())
        self.block_type = block_type
        self.content = content
        self.position = position
        self.output = None
        self.executed_at = None
        self.status = "pending"
        self.execution_time = None
        self.error_message = None
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

class Workflow:
    def __init__(self, name: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.blocks = []
        self.edges = []
        self.created_at = datetime.now(timezone.utc)
        self.execution_status = "pending"
        self.updated_at = datetime.now(timezone.utc)

# WebSocket manager for real-time communication
class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.workflow_subscriptions: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, workflow_id: Optional[str] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if workflow_id:
            if workflow_id not in self.workflow_subscriptions:
                self.workflow_subscriptions[workflow_id] = []
            self.workflow_subscriptions[workflow_id].append(websocket)
        
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, workflow_id: Optional[str] = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if workflow_id and workflow_id in self.workflow_subscriptions:
            if websocket in self.workflow_subscriptions[workflow_id]:
                self.workflow_subscriptions[workflow_id].remove(websocket)
        
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_to_workflow(self, workflow_id: str, message: Dict[str, Any]):
        """Broadcast message to clients subscribed to a specific workflow"""
        if workflow_id not in self.workflow_subscriptions:
            return
        
        disconnected = []
        for connection in self.workflow_subscriptions[workflow_id]:
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection, workflow_id)
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to a specific client"""
        try:
            await websocket.send_text(json.dumps(message))
        except:
            self.disconnect(websocket)

# Initialize WebSocket manager
websocket_manager = WebSocketManager()

# Initialize services (will be defined below)
python_executor = None
ai_tool_engine = None
dag_service = None
ai_agent = None

class PythonExecutorService:
    """Real Python execution service with persistent kernel and cell history"""
    
    def __init__(self):
        self.active_sessions = {}
        self.execution_history = {}
        self.global_variables = {}
        self.dataframes = {}
    
    async def start_session(self, session_id: str = None) -> str:
        """Start a new Python execution session"""
        if not session_id:
            session_id = f"session_{int(datetime.now(timezone.utc).timestamp())}"
        
        self.active_sessions[session_id] = {
            "variables": {},
            "dataframes": {},
            "imports": set(),
            "created_at": datetime.now(timezone.utc),
            "last_activity": datetime.now(timezone.utc)
        }
        
        self.execution_history[session_id] = []
        
        # Initialize with common imports
        initial_imports = "import pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns"
        session = self.active_sessions[session_id]
        session["imports"].add("import pandas as pd")
        session["imports"].add("import numpy as np") 
        session["imports"].add("import matplotlib.pyplot as plt")
        session["imports"].add("import seaborn as sns")
        
        # Execute the initial imports to verify they work
        await self._execute_code(initial_imports, session_id)
        
        return session_id
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get the current state of a session"""
        if session_id not in self.active_sessions:
            return {}
        
        session = self.active_sessions[session_id]
        return {
            "variables": session["variables"],
            "dataframes": list(session["dataframes"].keys()),
            "imports": list(session["imports"]),
            "last_activity": session["last_activity"].isoformat(),
            "execution_count": len(self.execution_history.get(session_id, [])),
            "created_at": session["created_at"].isoformat()
        }
    
    async def _execute_code(self, code: str, session_id: str) -> Dict[str, Any]:
        """Execute Python code in the session context"""
        try:
            # Create a temporary Python file with session context
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                # Add session context
                session = self.active_sessions[session_id]
                
                # Add imports
                import_lines = "\n".join(session["imports"])
                
                # Add global variables and dataframes
                var_lines = []
                for var_name, var_value in session["variables"].items():
                    if isinstance(var_value, str):
                        var_lines.append(f'{var_name} = "{var_value}"')
                    else:
                        var_lines.append(f'{var_name} = {var_value}')
                
                # Add dataframe variables
                for df_name, df_data in session["dataframes"].items():
                    var_lines.append(f'{df_name} = {df_data}')
                
                # Combine all code
                full_code = f"{import_lines}\n{chr(10).join(var_lines)}\n{code}"
                f.write(full_code)
                temp_file = f.name
            
            try:
                # Execute the code
                start_time = datetime.now(timezone.utc)
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                end_time = datetime.now(timezone.utc)
                
                execution_time = (end_time - start_time).total_seconds()
                
                if result.returncode == 0:
                    # Try to extract variables and dataframes from output
                    await self._extract_variables(code, session_id)
                    
                    return {
                        "success": True,
                        "output": result.stdout,
                        "error": result.stderr if result.stderr else None,
                        "execution_time": execution_time,
                        "session_id": session_id
                    }
                else:
                    return {
                        "success": False,
                        "output": None,
                        "error": result.stderr,
                        "execution_time": execution_time,
                        "session_id": session_id
                    }
                    
            finally:
                # Clean up temp file
                os.unlink(temp_file)
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": None,
                "error": "Execution timed out after 30 seconds",
                "execution_time": 30.0,
                "session_id": session_id
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e),
                "execution_time": 0.0,
                "session_id": session_id
            }
    
    async def execute_code(self, code: str, session_id: str = None) -> Dict[str, Any]:
        """Execute code and maintain session state"""
        if not session_id:
            session_id = await self.start_session()
        
        # Add to execution history
        self.execution_history[session_id].append({
            "code": code,
            "timestamp": datetime.now(timezone.utc),
            "status": "executing"
        })
        
        # Broadcast execution start
        workflow_id = session_id.replace("workflow_", "")
        await websocket_manager.broadcast_to_workflow(workflow_id, {
            "type": "execution_started",
            "session_id": session_id,
            "workflow_id": workflow_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Execute the code
        result = await self._execute_code(code, session_id)
        
        # Update history
        self.execution_history[session_id][-1]["status"] = "completed" if result["success"] else "failed"
        self.execution_history[session_id][-1]["result"] = result
        
        # Update session activity
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["last_activity"] = datetime.now(timezone.utc)
        
        # Broadcast execution result
        await websocket_manager.broadcast_to_workflow(workflow_id, {
            "type": "execution_completed",
            "session_id": session_id,
            "workflow_id": workflow_id,
            "success": result["success"],
            "output": result["output"],
            "error": result["error"],
            "execution_time": result["execution_time"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return result
    
    async def _extract_variables(self, code: str, session_id: str):
        """Extract variables and dataframes from executed code"""
        session = self.active_sessions[session_id]
        
        # Extract imports
        import_pattern = r'import\s+(\w+)'
        import_matches = re.findall(import_pattern, code)
        for import_name in import_matches:
            session["imports"].add(f"import {import_name}")
        
        # Also check for from imports
        from_import_pattern = r'from\s+(\w+)\s+import\s+(\w+)'
        from_import_matches = re.findall(from_import_pattern, code)
        for module_name, import_name in from_import_matches:
            session["imports"].add(f"from {module_name} import {import_name}")
        
        # Simple variable extraction (in a real implementation, you'd use AST parsing)
        # For demo purposes, we'll look for common patterns
        
        # Look for dataframe assignments
        df_pattern = r'(\w+)\s*=\s*pd\.DataFrame\(([^)]+)\)'
        df_matches = re.findall(df_pattern, code)
        for df_name, df_content in df_matches:
            if df_name not in ['pd', 'np', 'plt', 'sns']:  # Skip imports
                session["dataframes"][df_name] = f"pd.DataFrame({df_content})"
        
        # Look for variable assignments
        var_pattern = r'(\w+)\s*=\s*([^#\n]+)'
        var_matches = re.findall(var_pattern, code)
        for var_name, var_value in var_matches:
            if var_name not in ['pd', 'np', 'plt', 'sns'] and '=' not in var_value:  # Skip imports and complex assignments
                session["variables"][var_name] = var_value.strip()
        
        # Look for simple variable assignments like x = 5, name = "value"
        simple_var_pattern = r'(\w+)\s*=\s*([^#\n,]+?)(?:\s*[,#\n]|$)'
        simple_matches = re.findall(simple_var_pattern, code)
        for var_name, var_value in simple_matches:
            if var_name not in ['pd', 'np', 'plt', 'sns'] and var_name not in session["variables"]:
                # Try to evaluate the value
                try:
                    # For simple values like numbers, strings, etc.
                    if var_value.strip().isdigit():
                        session["variables"][var_name] = int(var_value.strip())
                    elif var_value.strip().replace('.', '').isdigit():
                        session["variables"][var_name] = float(var_value.strip())
                    elif var_value.strip().startswith('"') and var_value.strip().endswith('"'):
                        session["variables"][var_name] = var_value.strip().strip('"')
                    elif var_value.strip().startswith("'") and var_value.strip().endswith("'"):
                        session["variables"][var_name] = var_value.strip().strip("'")
                    else:
                        session["variables"][var_name] = var_value.strip()
                except:
                    session["variables"][var_name] = var_value.strip()
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get current session state"""
        if session_id not in self.active_sessions:
            return {}
        
        session = self.active_sessions[session_id]
        return {
            "variables": session["variables"],
            "dataframes": list(session["dataframes"].keys()),
            "imports": list(session["imports"]),
            "last_activity": session["last_activity"].isoformat(),
            "execution_count": len(self.execution_history.get(session_id, []))
        }

# Initialize services
python_executor = PythonExecutorService()

class AIToolEngine:
    """Real AI tool engine with comprehensive tools"""
    
    def __init__(self):
        self.tools = {}
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools"""
        self.tools = {
            "add_block": {
                "name": "Add Code Block",
                "description": "Add a new code block to the workflow",
                "parameters": ["content", "position_x", "position_y"],
                "examples": ["Add a data analysis block", "Create a visualization block"]
            },
            "edit_block": {
                "name": "Edit Code Block", 
                "description": "Edit an existing code block",
                "parameters": ["block_id", "new_content"],
                "examples": ["Modify the data cleaning block", "Update the analysis code"]
            },
            "delete_block": {
                "name": "Delete Code Block",
                "description": "Remove a code block from the workflow",
                "parameters": ["block_id"],
                "examples": ["Remove the failed block", "Delete unused analysis"]
            },
            "analyze_dataset": {
                "name": "Analyze Dataset",
                "description": "Analyze dataset and generate insights",
                "parameters": ["dataset_id"],
                "examples": ["Analyze the uploaded dataset", "Show dataset summary"]
            },
            "create_visualization": {
                "name": "Create Visualization",
                "description": "Generate charts and plots",
                "parameters": ["data_source", "chart_type"],
                "examples": ["Create a histogram", "Make a correlation plot"]
            },
            "clean_data": {
                "name": "Clean Data",
                "description": "Clean and preprocess data",
                "parameters": ["data_source", "cleaning_type"],
                "examples": ["Remove missing values", "Handle duplicates"]
            }
        }
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get all available tools"""
        return self.tools
    
    def suggest_tools_for_prompt(self, prompt: str) -> List[Dict[str, Any]]:
        """Suggest relevant tools based on user prompt"""
        relevant_tools = []
        
        prompt_lower = prompt.lower()
        
        for tool_name, tool in self.tools.items():
            if any(keyword in prompt_lower for keyword in tool.get("keywords", [])):
                relevant_tools.append({
                    "name": tool_name,
                    "description": tool["description"],
                    "examples": tool["examples"]
                })
        
        return relevant_tools

    def generate_blocks_from_tools(self, suggested_tools: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate code blocks based on suggested tools"""
        blocks = []
        
        for i, tool in enumerate(suggested_tools):
            if tool["name"] == "analyze_dataset":
                blocks.append({
                    "type": "code",
                    "content": "# Load and explore the dataset\nimport pandas as pd\n\ndf = pd.DataFrame(dataset_data)\nprint(f'Dataset shape: {df.shape}')\nprint('\\nFirst few rows:')\nprint(df.head())\n\nprint('\\nDataset info:')\ndf.info()\n\nprint('\\nBasic statistics:')\nprint(df.describe())",
                    "position": {"x": 100 + i * 200, "y": 100}
                })
            elif tool["name"] == "clean_data":
                blocks.append({
                    "type": "code",
                    "content": "# Data cleaning and preprocessing\nimport pandas as pd\n\n# Load the dataset\ndf = pd.DataFrame(dataset_data)\nprint(f\"Original dataset shape: {df.shape}\")\n\n# Remove duplicates\ndf_clean = df.drop_duplicates()\nprint(f\"Removed {len(df) - len(df_clean)} duplicate rows\")\n\n# Handle missing values\ndf_clean = df_clean.fillna(method=\"ffill\")\nprint(f\"Cleaned dataset shape: {df_clean.shape}\")\n\n# Show cleaned data\nprint(\"\\nFirst few rows of cleaned data:\")\nprint(df_clean.head())",
                    "position": {"x": 100 + i * 200, "y": 300}
                })
            elif tool["name"] == "create_visualization":
                blocks.append({
                    "type": "code",
                    "content": "# Create visualizations\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n\n# Load the dataset\ndf = pd.DataFrame(dataset_data)\n\nplt.figure(figsize=(15, 10))\n\n# Distribution plots for numerical columns\nnumerical_cols = df.select_dtypes(include=['number']).columns\nfor i, col in enumerate(numerical_cols[:4]):\n    plt.subplot(2, 2, i+1)\n    plt.hist(df[col].dropna(), bins=20, alpha=0.7)\n    plt.title(f'Distribution of {col}')\n    plt.xlabel(col)\n\nplt.tight_layout()\nplt.show()",
                    "position": {"x": 100 + i * 200, "y": 500}
                })
        
        # If no specific blocks generated, create default analysis block
        if not blocks:
            blocks.append({
                "type": "code",
                "content": "# Load and explore the dataset\nimport pandas as pd\n\ndf = pd.DataFrame(dataset_data)\nprint(f'Dataset shape: {df.shape}')\nprint('\\nFirst few rows:')\nprint(df.head())",
                "position": {"x": 100, "y": 100}
            })
        
        return blocks

class DAGService:
    """Real DAG service with automatic updates"""
    
    def __init__(self):
        self.executions = {}
        self.workflow_graphs = {}
    
    async def update_workflow_dag(self, workflow: Workflow) -> Dict[str, Any]:
        """Update DAG when workflow changes"""
        # Create nodes from blocks
        nodes = []
        for block in workflow.blocks:
            nodes.append({
                "id": block.id,
                "type": block.block_type,
                "position": block.position,
                "status": block.status,
                "content": block.content[:100] + "..." if len(block.content) > 100 else block.content
            })
        
        # Create edges based on block positions (left to right, top to bottom)
        edges = []
        sorted_blocks = sorted(workflow.blocks, key=lambda b: (b.position["y"], b.position["x"]))
        
        for i in range(len(sorted_blocks) - 1):
            edges.append({
                "id": f"edge_{i}",
                "source": sorted_blocks[i].id,
                "target": sorted_blocks[i + 1].id,
                "type": "default"
            })
        
        # Update workflow graph
        self.workflow_graphs[workflow.id] = {
            "nodes": nodes,
            "edges": edges,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Broadcast DAG update
        await websocket_manager.broadcast_to_workflow(workflow.id, {
            "type": "dag_updated",
            "workflow_id": workflow.id,
            "nodes": nodes,
            "edges": edges,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "workflow_id": workflow.id
        }
    
    def validate_workflow(self, blocks: List[Block]) -> Dict[str, Any]:
        """Validate workflow structure"""
        if not blocks:
            return {"is_valid": False, "error": "No blocks in workflow"}
        
        # Check for duplicate positions
        positions = set()
        for block in blocks:
            pos = (block.position["x"], block.position["y"])
            if pos in positions:
                return {"is_valid": False, "error": "Duplicate block positions"}
            positions.add(pos)
        
        # Check for cycles (simple check for demo)
        if len(blocks) > 1:
            # Simple validation - in real implementation, you'd use proper cycle detection
            return {"is_valid": True, "error": None, "warnings": ["Basic validation passed"]}
        
        return {"is_valid": True, "error": None}
    
    def create_execution_plan(self, blocks: List[Block]) -> List[str]:
        """Create execution order for blocks"""
        # Sort by position (left to right, top to bottom)
        sorted_blocks = sorted(blocks, key=lambda b: (b.position["y"], b.position["x"]))
        return [block.id for block in sorted_blocks]

ai_tool_engine = AIToolEngine()
dag_service = DAGService()

class MCPAIAgent:
    """Real MCP AI Agent with Ollama Qwen2.5:3b"""
    
    def __init__(self):
        self.tool_engine = AIToolEngine()
        self.model = "qwen2.5:3b"
        self.ollama_client = None
        self._initialize_ollama()
    
    def _initialize_ollama(self):
        """Initialize Ollama client"""
        try:
            import ollama
            
            # Test Ollama connection
            models_response = ollama.list()
            available_models = [model.model for model in models_response.models]
            
            if self.model not in available_models:
                print(f"Model {self.model} not found. Available models: {available_models}")
                if available_models:
                    self.model = available_models[0]  # Use first available model
                    print(f"Using model: {self.model}")
            
            self.ollama_client = ollama
            print(f"Ollama initialized with model: {self.model}")
            
        except Exception as e:
            print(f"Failed to initialize Ollama: {e}")
            self.ollama_client = None
    
    async def process_request(
        self, 
        user_request: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process user request using AI"""
        try:
            if not self.ollama_client:
                return {
                    "success": False,
                    "error": "Ollama not available",
                    "fallback_response": self._generate_fallback_response(user_request, context)
                }
            
            # Build context-aware prompt
            prompt = self._build_prompt(user_request, context)
            
            # Generate AI response
            response = await asyncio.to_thread(
                self.ollama_client.chat,
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                options={
                    'temperature': 0.7,
                    'num_predict': 1000,
                }
            )
            
            ai_response = response['message']['content']
            
            # Parse AI response and generate actions
            actions = self._parse_ai_response(ai_response, context)
            
            return {
                "success": True,
                "ai_response": ai_response,
                "actions": actions,
                "model_used": self.model
            }
            
        except Exception as e:
            print(f"AI processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_response": self._generate_fallback_response(user_request, context)
            }
    
    def _build_prompt(self, user_request: str, context: Dict[str, Any]) -> str:
        """Build context-aware prompt for AI"""
        prompt = f"""You are an AI assistant for a data science notebook system. 

Current context:
- Dataset: {context.get('dataset_info', 'No dataset')}
- Current blocks: {len(context.get('blocks', []))} blocks
- Workflow status: {context.get('workflow_status', 'No workflow')}

User request: {user_request}

Available tools: {list(self.tool_engine.tools.keys())}

IMPORTANT: When generating code blocks, ALWAYS include the necessary imports at the top of each block.
For data analysis, ALWAYS include: import pandas as pd
For visualizations, ALWAYS include: import matplotlib.pyplot as plt, import seaborn as sns

Please provide a response that:
1. Understands what the user wants
2. Suggests specific actions using available tools
3. Provides clear, actionable steps
4. If adding/editing blocks, provide the actual code content with proper imports

Example of good code block:
```python
# Data cleaning and preprocessing
import pandas as pd

# Load the dataset
df = pd.DataFrame(dataset_data)
print(f"Original dataset shape: {df.shape}")

# Your analysis code here
```

Respond in a helpful, technical manner suitable for data scientists."""

        return prompt
    
    def _parse_ai_response(self, ai_response: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse AI response and generate actionable steps"""
        actions = []
        
        # Look for code blocks in markdown format
        code_block_pattern = r'```python\n(.*?)\n```'
        code_matches = re.findall(code_block_pattern, ai_response, re.DOTALL)
        
        if code_matches:
            for i, code_content in enumerate(code_matches):
                actions.append({
                    "type": "add_block",
                    "content": code_content.strip(),
                    "position": {"x": 100 + (i * 200), "y": 300}
                })
        else:
            # Fallback: look for code patterns in the response
            if "clean" in ai_response.lower() or "data" in ai_response.lower():
                actions.append({
                    "type": "add_block",
                    "content": "# Data cleaning and preprocessing\nimport pandas as pd\n\n# Load the dataset\ndf = pd.DataFrame(dataset_data)\nprint(f\"Original dataset shape: {df.shape}\")\n\n# Remove duplicates\ndf_clean = df.drop_duplicates()\nprint(f\"Removed {len(df) - len(df_clean)} duplicate rows\")\n\n# Handle missing values\ndf_clean = df_clean.fillna(method=\"ffill\")\nprint(f\"Cleaned dataset shape: {df_clean.shape}\")\n\n# Show cleaned data\nprint(\"\\nFirst few rows of cleaned data:\")\nprint(df_clean.head())",
                    "position": {"x": 100, "y": 300}
                })
            
            if "mean" in ai_response.lower() or "price" in ai_response.lower():
                actions.append({
                    "type": "add_block",
                    "content": "# Calculate mean of price column\nimport pandas as pd\n\n# Load the dataset\ndf = pd.DataFrame(dataset_data)\n\n# Calculate mean price\nmean_price = df[\"price\"].mean()\nprint(f\"Mean price: ${mean_price:.2f}\")\n\n# Show price statistics\nprint(\"\\nPrice statistics:\")\nprint(df[\"price\"].describe())",
                    "position": {"x": 300, "y": 300}
                })
        
        return actions
    
    def _generate_fallback_response(self, user_request: str, context: Dict[str, Any]) -> str:
        """Generate fallback response when AI is not available"""
        if "analyze" in user_request.lower():
            return "I'll help you analyze the dataset. Let me create some analysis blocks."
        elif "visualize" in user_request.lower():
            return "I'll create visualization blocks for your data."
        elif "clean" in user_request.lower():
            return "I'll add data cleaning blocks to your workflow."
        else:
            return "I'll help you with your request. Let me add some appropriate blocks to your workflow."

ai_agent = MCPAIAgent()

@app.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload a CSV dataset"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        dataset_id = str(uuid.uuid4())
        # Convert dtypes to strings to avoid serialization issues
        column_types = {}
        for col in df.columns:
            column_types[col] = str(df[col].dtype)
        
        datasets[dataset_id] = {
            "id": dataset_id,
            "name": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "data": df.to_dict('records'),
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "file_size": len(content),
            "column_types": column_types,
            "sample_data": df.head().to_dict('records')
        }
        
        return {
            "success": True,
            "dataset_id": dataset_id,
            "message": f"Dataset uploaded successfully: {len(df)} rows, {len(df.columns)} columns",
            "dataset_info": {
                "name": file.filename,
                "rows": len(df),
                "columns": list(df.columns),
                "column_types": column_types,
                "sample_data": df.head().to_dict('records')
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading dataset: {str(e)}")

@app.get("/datasets")
async def get_datasets():
    """Get all uploaded datasets"""
    return {
        "success": True,
        "datasets": list(datasets.values())
    }

@app.get("/ai/tools")
async def get_ai_tools():
    """Get available AI tools"""
    return {
        "success": True,
        "tools": ai_tool_engine.get_available_tools()
    }

@app.post("/ai/process")
async def process_ai_request(request: Dict[str, Any]):
    """Process AI request and generate blocks/workflow"""
    try:
        user_prompt = request.get("prompt", "")
        dataset_id = request.get("dataset_id")
        
        if not user_prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        if not dataset_id or dataset_id not in datasets:
            raise HTTPException(status_code=400, detail="Valid dataset ID is required")
        
        # Get context for AI
        context = {
            "dataset_info": datasets[dataset_id],
            "blocks": [],
            "workflow_status": "new"
        }
        
        # Use the AI agent to generate blocks
        try:
            ai_response = await ai_agent.process_request(user_prompt, context)
            
            if ai_response and ai_response.get("success") and ai_response.get("actions"):
                # Convert AI actions to blocks
                generated_blocks = []
                for action in ai_response["actions"]:
                    if action["type"] == "add_block":
                        generated_blocks.append({
                            "type": "code",
                            "content": action["content"],
                            "position": action["position"]
                        })
            else:
                # Fallback to tool-based generation if AI fails
                suggested_tools = ai_tool_engine.suggest_tools_for_prompt(user_prompt)
                generated_blocks = ai_tool_engine.generate_blocks_from_tools(suggested_tools, context)
        except Exception as e:
            print(f"AI processing error: {e}")
            # Fallback to tool-based generation
            suggested_tools = ai_tool_engine.suggest_tools_for_prompt(user_prompt)
            generated_blocks = ai_tool_engine.generate_blocks_from_tools(suggested_tools, context)
        
        # Create workflow
        workflow = Workflow(f"AI Generated: {user_prompt[:50]}...")
        
        # Add blocks to workflow
        for block_data in generated_blocks:
            block = Block(
                block_type=block_data["type"],
                content=block_data["content"],
                position=block_data["position"]
            )
            workflow.blocks.append(block)
            blocks[block.id] = block
        
        workflows[workflow.id] = workflow
        
        # Update DAG
        await dag_service.update_workflow_dag(workflow)
        
        # Validate workflow
        validation = dag_service.validate_workflow(workflow.blocks)
        execution_plan = dag_service.create_execution_plan(workflow.blocks)
        
        return {
            "success": True,
            "workflow_id": workflow.id,
            "blocks": [{"id": b.id, "type": b.block_type, "content": b.content, "position": b.position} for b in workflow.blocks],
            "dag_info": dag_service.workflow_graphs.get(workflow.id, {}),
            "validation": validation,
            "execution_plan": execution_plan,
            "message": f"Generated {len(generated_blocks)} blocks based on your request"
        }
        
    except Exception as e:
        print(f"AI processing error: {e}")
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

@app.get("/workflows")
async def get_workflows():
    """Get all workflows"""
    try:
        workflow_list = []
        for workflow in workflows.values():
            workflow_list.append({
                "id": workflow.id,
                "name": workflow.name,
                "blocks_count": len(workflow.blocks),
                "created_at": workflow.created_at.isoformat(),
                "execution_status": workflow.execution_status,
                "updated_at": workflow.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "workflows": workflow_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting workflows: {str(e)}")

@app.get("/workflows/{workflow_id}/blocks")
async def get_workflow_blocks(workflow_id: str):
    """Get all blocks for a workflow"""
    try:
        if workflow_id not in workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow = workflows[workflow_id]
        blocks_list = []
        
        for block in workflow.blocks:
            blocks_list.append({
                "id": block.id,
                "type": block.block_type,
                "content": block.content,
                "position": block.position,
                "output": block.output,
                "status": block.status,
                "execution_time": block.execution_time,
                "error_message": block.error_message,
                "executed_at": block.executed_at.isoformat() if block.executed_at else None,
                "created_at": block.created_at.isoformat(),
                "updated_at": block.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "blocks": blocks_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting workflow blocks: {str(e)}")

@app.get("/workflows/{workflow_id}/session")
async def get_workflow_session(workflow_id: str):
    """Get current session state for a workflow"""
    try:
        if workflow_id not in workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        session_id = f"workflow_{workflow_id}"
        if session_id not in python_executor.active_sessions:
            return {
                "success": True,
                "session_id": session_id,
                "status": "not_started",
                "session_state": None
            }
        
        session_state = python_executor.get_session_state(session_id)
        return {
            "success": True,
            "session_id": session_id,
            "status": "active",
            "session_state": session_state
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session: {str(e)}")

@app.get("/workflows/{workflow_id}/execution-history")
async def get_workflow_execution_history(workflow_id: str):
    """Get execution history for a workflow"""
    try:
        if workflow_id not in workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        session_id = f"workflow_{workflow_id}"
        if session_id not in python_executor.active_sessions:
            return {
                "success": True,
                "execution_history": []
            }
        
        workflow = workflows[workflow_id]
        execution_history = []
        
        for block in workflow.blocks:
            if block.executed_at:
                execution_history.append({
                    "block_id": block.id,
                    "block_content": block.content[:100] + "..." if len(block.content) > 100 else block.content,
                    "status": block.status,
                    "execution_time": block.execution_time,
                    "executed_at": block.executed_at.isoformat(),
                    "output": block.output,
                    "error_message": block.error_message
                })
        
        # Sort by execution time
        execution_history.sort(key=lambda x: x["executed_at"])
        
        return {
            "success": True,
            "execution_history": execution_history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting execution history: {str(e)}")

@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow by ID"""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    validation = dag_service.validate_workflow(workflow.blocks)
    execution_plan = dag_service.create_execution_plan(workflow.blocks)
    dag_info = await dag_service.update_workflow_dag(workflow)
    
    return {
        "success": True,
        "workflow": {
            "id": workflow.id,
            "name": workflow.name,
            "blocks": [{"id": b.id, "type": b.block_type, "content": b.content, "position": b.position, "output": b.output, "status": b.status, "execution_time": b.execution_time, "error_message": b.error_message} for b in workflow.blocks],
            "edges": workflow.edges,
            "created_at": workflow.created_at.isoformat(),
            "execution_status": workflow.execution_status,
            "validation": validation,
            "execution_plan": execution_plan,
            "dag_info": dag_info
        }
    }

@app.post("/blocks/{block_id}/execute")
async def execute_block(block_id: str):
    """Execute a single block"""
    try:
        if block_id not in blocks:
            raise HTTPException(status_code=404, detail="Block not found")
        
        block = blocks[block_id]
        
        # Find which workflow this block belongs to
        workflow_id = None
        for workflow in workflows.values():
            if any(b.id == block_id for b in workflow.blocks):
                workflow_id = workflow.id
                break
        
        if not workflow_id:
            raise HTTPException(status_code=400, detail="Block does not belong to any workflow")
        
        # Use workflow-based session ID to maintain context across blocks
        session_id = f"workflow_{workflow_id}"
        if session_id not in python_executor.active_sessions:
            await python_executor.start_session(session_id)
        
        # Get dataset context for this workflow
        dataset_data = None
        if datasets:
            first_dataset = list(datasets.values())[0]
            dataset_data = first_dataset["data"]
        
        # Execute the Python code with dataset context
        if dataset_data:
            # Inject dataset data into the session if not already present
            session = python_executor.active_sessions.get(session_id)
            if session and "dataset_data" not in session["dataframes"]:
                # Convert the dataset data to a proper format for pandas
                # dataset_data is a list of dictionaries, so we need to format it properly
                session["dataframes"]["dataset_data"] = str(dataset_data)
                print(f"Injected dataset data into workflow session {session_id}")
                print(f"Dataset data type: {type(dataset_data)}, length: {len(dataset_data)}")
        
        execution_result = await python_executor.execute_code(block.content, session_id)
        
        if execution_result["success"]:
            block.output = execution_result["output"]
            block.status = "completed"
            block.execution_time = execution_result["execution_time"]
            block.error_message = None
        else:
            block.output = None
            block.status = "failed"
            block.execution_time = execution_result["execution_time"]
            block.error_message = execution_result["error"]
        
        block.executed_at = datetime.now(timezone.utc)
        
        # Update DAG if this block is part of a workflow
        for workflow in workflows.values():
            if any(b.id == block_id for b in workflow.blocks):
                await dag_service.update_workflow_dag(workflow)
                break
        
        # Broadcast block execution result
        await websocket_manager.broadcast_to_workflow(workflow_id, {
            "type": "block_executed",
            "block_id": block_id,
            "workflow_id": workflow_id,
            "status": block.status,
            "output": block.output,
            "error_message": block.error_message,
            "execution_time": block.execution_time,
            "executed_at": block.executed_at.isoformat(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "success": True,
            "block_id": block_id,
            "workflow_id": workflow_id,
            "session_id": session_id,
            "output": block.output,
            "status": block.status,
            "execution_time": block.execution_time,
            "error_message": block.error_message,
            "executed_at": block.executed_at.isoformat(),
            "session_state": python_executor.get_session_state(session_id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing block: {str(e)}")

@app.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str):
    """Execute entire workflow"""
    try:
        if workflow_id not in workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow = workflows[workflow_id]
        workflow.execution_status = "running"
        
        # Get execution plan
        execution_plan = dag_service.create_execution_plan(workflow.blocks)
        results = []
        
        # Execute blocks in order
        for block_id in execution_plan:
            result = await execute_block(block_id)
            results.append(result)
            
            # Small delay between blocks for demo effect
            await asyncio.sleep(0.5)
        
        workflow.execution_status = "completed"
        workflow.updated_at = datetime.now(timezone.utc)
        
        # Update DAG
        await dag_service.update_workflow_dag(workflow)
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "results": results,
            "execution_plan": execution_plan,
            "message": f"Workflow executed successfully: {len(results)} blocks processed",
            "total_execution_time": sum(r.get("execution_time", 0) for r in results),
            "dag_info": dag_service.workflow_graphs.get(workflow_id, {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing workflow: {str(e)}")

@app.post("/blocks")
async def create_block(request: Dict[str, Any]):
    """Create a new block"""
    try:
        content = request.get("content", "")
        position = request.get("position", {"x": 100, "y": 100})
        block_type = request.get("type", "code")
        
        block = Block(block_type, content, position)
        blocks[block.id] = block
        
        return {
            "success": True,
            "block": {
                "id": block.id,
                "type": block.block_type,
                "content": block.content,
                "position": block.position,
                "created_at": block.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating block: {str(e)}")

@app.put("/blocks/{block_id}")
async def update_block(block_id: str, request: Dict[str, Any]):
    """Update an existing block"""
    try:
        if block_id not in blocks:
            raise HTTPException(status_code=404, detail="Block not found")
        
        block = blocks[block_id]
        block.content = request.get("content", block.content)
        block.position = request.get("position", block.position)
        block.updated_at = datetime.now(timezone.utc)
        
        return {
            "success": True,
            "block": {
                "id": block.id,
                "type": block.block_type,
                "content": block.content,
                "position": block.position,
                "updated_at": block.updated_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating block: {str(e)}")

@app.delete("/blocks/{block_id}")
async def delete_block(block_id: str):
    """Delete a block"""
    try:
        if block_id not in blocks:
            raise HTTPException(status_code=404, detail="Block not found")
        
        # Remove from blocks
        deleted_block = blocks.pop(block_id)
        
        # Remove from workflows
        for workflow in workflows.values():
            workflow.blocks = [b for b in workflow.blocks if b.id != block_id]
            if workflow.blocks:
                await dag_service.update_workflow_dag(workflow)
        
        return {
            "success": True,
            "message": f"Block {block_id} deleted successfully",
            "deleted_block": {
                "id": deleted_block.id,
                "type": deleted_block.block_type
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting block: {str(e)}")

@app.post("/workflows/{workflow_id}/blocks")
async def add_block_to_workflow(workflow_id: str, block_data: Dict[str, Any]):
    """Add a new block to a workflow"""
    try:
        if workflow_id not in workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow = workflows[workflow_id]
        
        # Create new block
        new_block = Block(
            block_type=block_data.get("type", "code"),
            content=block_data.get("content", "# New code block"),
            position=block_data.get("position", {"x": 100, "y": 100})
        )
        
        # Add to workflow and blocks collection
        workflow.blocks.append(new_block)
        blocks[new_block.id] = new_block
        
        # Update DAG
        dag_info = await dag_service.update_workflow_dag(workflow)
        
        # Broadcast DAG update
        await websocket_manager.broadcast_to_workflow(workflow_id, {
            "type": "dag_updated",
            "workflow_id": workflow_id,
            "nodes": [{"id": b.id, "content": b.content, "position": b.position, "type": b.block_type, "status": b.status} for b in workflow.blocks],
            "edges": dag_info.get("edges", [])
        })
        
        return {
            "success": True,
            "block_id": new_block.id,
            "message": "Block added successfully"
        }
        
    except Exception as e:
        print(f"Error adding block: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding block: {str(e)}")

@app.get("/system/status")
async def get_system_status():
    """Get system status and metrics"""
    return {
        "success": True,
        "status": "running",
        "metrics": {
            "datasets_count": len(datasets),
            "blocks_count": len(blocks),
            "workflows_count": len(workflows),
            "active_executions": 0,  # Could track this in real-time
            "completed_executions": sum(1 for b in blocks.values() if b.executed_at),
            "failed_executions": sum(1 for b in blocks.values() if b.status == "failed"),
            "python_sessions": len(python_executor.active_sessions) if python_executor else 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "services": {
            "python_executor": "active",
            "ai_tool_engine": "active", 
            "dag_service": "active",
            "ai_agent": "active" if ai_agent.ollama_client else "inactive"
        },
        "ai_model": ai_agent.model if ai_agent.ollama_client else "not available",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.websocket("/ws/test")
async def test_websocket_endpoint(websocket: WebSocket):
    """Simple test WebSocket endpoint"""
    await websocket.accept()
    await websocket.send_text("Hello from WebSocket!")
    await websocket.close()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """General WebSocket endpoint for system-wide updates"""
    await websocket.accept()
    print(f"✅ WebSocket connected. Total connections: {len(websocket_manager.active_connections) + 1}")
    
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message.get("type") == "subscribe_workflow":
                workflow_id = message.get("workflow_id")
                if workflow_id:
                    await websocket_manager.connect(websocket, workflow_id)
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "workflow_id": workflow_id
                    }))
                    
    except WebSocketDisconnect:
        print("❌ WebSocket disconnected")
        websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        websocket_manager.disconnect(websocket)

@app.websocket("/ws/workflow/{workflow_id}")
async def workflow_websocket_endpoint(websocket: WebSocket, workflow_id: str):
    """Workflow-specific WebSocket endpoint for real-time updates"""
    await websocket.accept()
    print(f"✅ Workflow WebSocket connected for workflow: {workflow_id}")
    
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message.get("type") == "get_workflow_status":
                if workflow_id in workflows:
                    workflow = workflows[workflow_id]
                    await websocket.send_text(json.dumps({
                        "type": "workflow_status",
                        "workflow_id": workflow_id,
                        "status": workflow.execution_status,
                        "blocks_count": len(workflow.blocks),
                        "completed_blocks": len([b for b in workflow.blocks if b.status == "completed"])
                    }))
                    
    except WebSocketDisconnect:
        print(f"❌ Workflow WebSocket disconnected for workflow: {workflow_id}")
        websocket_manager.disconnect(websocket, workflow_id)
    except Exception as e:
        print(f"❌ Workflow WebSocket error: {e}")
        websocket_manager.disconnect(websocket, workflow_id)

# Background task to broadcast system metrics
async def broadcast_system_metrics():
    """Periodically broadcast system metrics to all connected clients"""
    while True:
        try:
            metrics = {
                "type": "system_metrics",
                "datasets_count": len(datasets),
                "blocks_count": len(blocks),
                "workflows_count": len(workflows),
                "active_executions": 0,  # Could track this in real-time
                "completed_executions": sum(1 for b in blocks.values() if b.executed_at),
                "failed_executions": sum(1 for b in blocks.values() if b.status == "failed"),
                "python_sessions": len(python_executor.active_sessions) if python_executor else 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            await websocket_manager.broadcast_to_all(metrics)
            
        except Exception as e:
            print(f"Error broadcasting system metrics: {e}")
        
        await asyncio.sleep(5)  # Update every 5 seconds

@app.get("/")
async def root():
    return {"message": "AI Notebook Demo Backend", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
