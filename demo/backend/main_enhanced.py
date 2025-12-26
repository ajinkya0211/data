"""
Enhanced AI Notebook Backend with MCP Integration
Integrates MCP system, DAG system, and Python executor for powerful AI capabilities
"""

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
import logging
import traceback
from contextlib import asynccontextmanager

# Import our enhanced systems
from mcp_system import agent_manager, initialize_mcp_system, shutdown_mcp_system, NotebookContext
from dag_system import DAGManager, BlockStatus
from python_executor import python_executor, ExecutionResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI"""
    # Startup
    print("🚀 Starting Enhanced AI Notebook Backend...")
    print("🔧 Initializing MCP system...")
    await initialize_mcp_system()
    
    # Start background tasks
    task = asyncio.create_task(broadcast_system_metrics())
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Enhanced AI Notebook Backend...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    await shutdown_mcp_system()

# Create FastAPI app with lifespan
app = FastAPI(
    title="Enhanced AI Notebook with MCP", 
    version="2.0.0",
    description="AI-powered notebook system with MCP integration and multi-agent architecture",
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

# Global storage
datasets = {}
workflows = {}
notebook_contexts = {}

# Initialize DAG manager
dag_manager = DAGManager()

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

# Initialize WebSocket manager
websocket_manager = WebSocketManager()

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
            "sample_data": df.head().to_dict('records'),
            "summary_stats": df.describe().to_dict() if df.select_dtypes(include=['number']).shape[1] > 0 else {}
        }
        
        return {
            "success": True,
            "dataset_id": dataset_id,
            "message": f"Dataset uploaded successfully: {len(df)} rows, {len(df.columns)} columns",
            "dataset_info": datasets[dataset_id]
        }
    except Exception as e:
        logger.error(f"Error uploading dataset: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading dataset: {str(e)}")

@app.get("/datasets")
async def get_datasets():
    """Get all uploaded datasets"""
    return {
        "success": True,
        "datasets": list(datasets.values())
    }

@app.post("/ai/process")
async def process_ai_request(request: Dict[str, Any]):
    """Process AI request using MCP system and generate blocks/workflow"""
    try:
        user_prompt = request.get("message", "") or request.get("prompt", "")
        dataset_id = request.get("dataset_id")
        
        if not user_prompt:
            raise HTTPException(status_code=400, detail="Message or prompt is required")
        
        # Make dataset_id optional for now
        # if not dataset_id or dataset_id not in datasets:
        #     raise HTTPException(status_code=400, detail="Valid dataset ID is required")
        
        # Create notebook context
        context = NotebookContext()
        
        # Handle dataset info safely
        dataset_info = None
        if dataset_id and dataset_id in datasets:
            dataset_info = datasets[dataset_id]
        
        context.update_context(
            workflow_id=str(uuid.uuid4()),
            dataset_info=dataset_info
        )
        
        # For now, let's create a simple AI response without the complex agent system
        # This will allow us to test the basic functionality
        
        # Generate a simple code block based on the prompt
        if "hello" in user_prompt.lower() or "world" in user_prompt.lower():
            generated_code = '''# Hello World Example
print("Hello, World!")
print("Welcome to the AI Notebook!")

# Basic variable assignment
message = "This code was generated by AI"
print(f"AI Message: {message}")'''
        elif "data" in user_prompt.lower() or "analysis" in user_prompt.lower():
            generated_code = '''# Data Analysis Example
import pandas as pd
import numpy as np

# Create sample data
data = pd.DataFrame({
    'x': np.random.randn(100),
    'y': np.random.randn(100)
})

# Basic analysis
print("Data shape:", data.shape)
print("Data head:")
print(data.head())

# Summary statistics
print("\\nSummary statistics:")
print(data.describe())'''
        else:
            generated_code = f'''# AI Generated Code
# Based on your request: {user_prompt}

# This is a placeholder code block
# You can modify it based on your needs

print("AI generated this code block for you!")
print(f"Your request was: {user_prompt}")

# Add your custom logic here
def process_request(request):
    return f"Processing: {request}"

result = process_request(user_prompt)
print(f"Result: {result}")'''

        # Create a mock agent response
        generated_blocks = [{
            "id": str(uuid.uuid4()),
            "type": "code",
            "content": generated_code,
            "position": {"x": 100, "y": 100}
        }]
        
        # Process generated blocks
        for i, block_data in enumerate(generated_blocks):
            # Add block to DAG
            block_id = dag_manager.add_block(block_data)
            generated_blocks[i]["id"] = block_id
            
            # Add to context
            context.add_block(block_data)
        
        # Create workflow
        workflow_id = context.workflow_id
        workflows[workflow_id] = {
            "id": workflow_id,
            "name": f"AI Generated: {user_prompt[:50]}...",
            "blocks": generated_blocks,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "execution_status": "pending"
        }
        
        # Store context
        notebook_contexts[workflow_id] = context
        
        # Get DAG information
        dag_info = dag_manager.get_dag_visualization_data()
        execution_plan = dag_manager.get_execution_plan()
        validation = dag_manager.validate_workflow()
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "blocks": generated_blocks,
            "dag_info": dag_info,
            "execution_plan": execution_plan,
            "validation": validation,
            "response": f"AI generated {len(generated_blocks)} code blocks based on your request: '{user_prompt}'",
            "code_blocks": [
                {
                    "code": block["content"],
                    "description": f"AI generated code block for: {user_prompt}"
                }
                for block in generated_blocks
            ]
        }
        
    except Exception as e:
        logger.error(f"AI processing error: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

def _extract_code_blocks(content: str) -> List[str]:
    """Extract Python code blocks from AI response"""
    code_blocks = []
    
    # Look for markdown code blocks
    import re
    pattern = r'```python\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    if matches:
        code_blocks.extend(matches)
    else:
        # Look for code patterns in the response
        if "import" in content or "pd." in content or "plt." in content:
            # Extract lines that look like code
            lines = content.split('\n')
            code_lines = []
            for line in lines:
                line = line.strip()
                if (line.startswith('import') or 
                    line.startswith('from') or 
                    line.startswith('def') or
                    line.startswith('class') or
                    '=' in line or
                    'pd.' in line or
                    'plt.' in line or
                    'np.' in line):
                    code_lines.append(line)
            
            if code_lines:
                code_blocks.append('\n'.join(code_lines))
    
    # If no code blocks found, create a basic analysis block
    if not code_blocks:
        code_blocks.append("""# Data Analysis Block
import pandas as pd
import numpy as np

# Load and explore the dataset
print("Dataset loaded successfully")
print("Ready for analysis")""")
    
    return code_blocks

@app.post("/workflows")
async def create_workflow(workflow_data: Dict[str, Any]):
    """Create a new workflow"""
    try:
        workflow_id = str(uuid.uuid4())
        workflows[workflow_id] = {
            "id": workflow_id,
            "name": workflow_data.get("name", "Untitled Workflow"),
            "description": workflow_data.get("description", ""),
            "blocks": workflow_data.get("blocks", []),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "execution_status": "pending"
        }
        
        return {
            "success": True,
            "workflow": workflows[workflow_id]
        }
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating workflow: {str(e)}")

@app.get("/workflows")
async def get_workflows():
    """Get all workflows"""
    try:
        workflow_list = []
        for workflow_id, workflow in workflows.items():
            workflow_list.append({
                "id": workflow_id,
                "name": workflow["name"],
                "blocks_count": len(workflow["blocks"]),
                "created_at": workflow["created_at"],
                "execution_status": workflow["execution_status"],
                "dag_status": dag_manager.get_system_status()
            })
        
        return {
            "success": True,
            "workflows": workflow_list
        }
        
    except Exception as e:
        logger.error(f"Error getting workflows: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting workflows: {str(e)}")

@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow by ID with full DAG information"""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    
    # Get DAG information
    dag_info = dag_manager.get_dag_visualization_data()
    execution_plan = dag_manager.get_execution_plan()
    validation = dag_manager.validate_workflow()
    
    return {
        "success": True,
        "workflow": {
            "id": workflow_id,
            "name": workflow["name"],
            "blocks": workflow["blocks"],
            "created_at": workflow["created_at"],
            "execution_status": workflow["execution_status"],
            "dag_info": dag_info,
            "execution_plan": execution_plan,
            "validation": validation
        }
    }

@app.post("/workflows/{workflow_id}/blocks")
async def add_block_to_workflow(workflow_id: str, block_data: Dict[str, Any]):
    """Add a new block to a workflow"""
    try:
        if workflow_id not in workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Generate block ID
        block_id = str(uuid.uuid4())
        block_data["id"] = block_id
        
        # Add block to workflow
        workflows[workflow_id]["blocks"].append(block_data)
        
        # Add block to DAG
        dag_manager.add_block(block_data)
        
        return {
            "success": True,
            "block": block_data
        }
        
    except Exception as e:
        logger.error(f"Error adding block to workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding block to workflow: {str(e)}")

@app.get("/workflows/{workflow_id}/blocks")
async def get_workflow_blocks(workflow_id: str):
    """Get all blocks for a workflow with dependency information"""
    try:
        if workflow_id not in workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow = workflows[workflow_id]
        blocks_list = []
        
        for block in workflow["blocks"]:
            block_id = block["id"]
            dependencies = dag_manager.get_block_dependencies(block_id)
            
            blocks_list.append({
                "id": block_id,
                "type": block["type"],
                "content": block["content"],
                "position": block["position"],
                "dependencies": dependencies.get("dependencies", []),
                "dependents": dependencies.get("dependents", []),
                "execution_order": dependencies.get("execution_order"),
                "status": dependencies.get("status", "pending")
            })
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "blocks": blocks_list
        }
        
    except Exception as e:
        logger.error(f"Error getting workflow blocks: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting workflow blocks: {str(e)}")

@app.post("/blocks/{block_id}/execute")
async def execute_block(block_id: str):
    """Execute a single block"""
    try:
        # Find which workflow this block belongs to
        workflow_id = None
        for wf_id, workflow in workflows.items():
            if any(b["id"] == block_id for b in workflow["blocks"]):
                workflow_id = wf_id
                break
        
        # If no workflow found, create a temporary one for standalone blocks
        if not workflow_id:
            workflow_id = f"standalone_{block_id}"
            workflows[workflow_id] = {
                "id": workflow_id,
                "name": f"Standalone Block: {block_id[:8]}...",
                "blocks": [{"id": block_id, "type": "code", "content": "", "position": {"x": 100, "y": 100}}],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "execution_status": "pending"
            }
        
        # Get block content from DAG manager
        block_node = dag_manager.blocks.get(block_id)
        if not block_node:
            raise HTTPException(status_code=404, detail="Block not found in DAG")
        
        block_content = block_node.content
        
        # Get dataset context
        context = {}
        if workflow_id in notebook_contexts:
            context = notebook_contexts[workflow_id].to_dict()
        
        # Execute the code
        execution_result = await python_executor.execute_code(
            block_content,
            session_id=f"workflow_{workflow_id}",
            context=context
        )
        
        # Update DAG status
        dag_manager.update_block(block_id, {
            "status": BlockStatus.COMPLETED if execution_result.success else BlockStatus.FAILED
        })
        
        # Broadcast execution result
        await websocket_manager.broadcast_to_workflow(workflow_id, {
            "type": "block_executed",
            "block_id": block_id,
            "workflow_id": workflow_id,
            "success": execution_result.success,
            "output": execution_result.output,
            "error": execution_result.error,
            "execution_time": execution_result.execution_time,
            "timestamp": execution_result.timestamp.isoformat()
        })
        
        return {
            "success": True,
            "block_id": block_id,
            "workflow_id": workflow_id,
            "execution_result": {
                "success": execution_result.success,
                "output": execution_result.output,
                "error": execution_result.error,
                "execution_time": execution_result.execution_time,
                "variables_defined": execution_result.variables_defined,
                "imports_added": execution_result.imports_added
            },
            "session_state": python_executor.get_session_state(f"workflow_{workflow_id}")
        }
        
    except Exception as e:
        logger.error(f"Error executing block: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error executing block: {str(e)}")

@app.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str):
    """Execute entire workflow"""
    try:
        if workflow_id not in workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow = workflows[workflow_id]
        workflow["execution_status"] = "running"
        
        # Get execution plan from DAG
        execution_plan = dag_manager.get_execution_plan()
        results = []
        
        # Execute blocks in order
        for plan_item in execution_plan:
            block_id = plan_item["block_id"]
            
            # Execute block
            result = await execute_block(block_id)
            results.append(result)
            
            # Small delay between blocks
            await asyncio.sleep(0.5)
        
        workflow["execution_status"] = "completed"
        
        # Update DAG
        dag_info = dag_manager.get_dag_visualization_data()
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "results": results,
            "execution_plan": execution_plan,
            "message": f"Workflow executed successfully: {len(results)} blocks processed",
            "dag_info": dag_info
        }
        
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Error executing workflow: {str(e)}")

@app.post("/blocks")
async def create_block(request: Dict[str, Any]):
    """Create a new block"""
    try:
        content = request.get("content", "")
        position = request.get("position", {"x": 100, "y": 100})
        block_type = request.get("type", "code")
        
        # Add block to DAG
        block_data = {
            "type": block_type,
            "content": content,
            "position": position
        }
        
        block_id = dag_manager.add_block(block_data)
        
        return {
            "success": True,
            "block_id": block_id,
            "block": {
                "id": block_id,
                **block_data
            }
        }
    except Exception as e:
        logger.error(f"Error creating block: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating block: {str(e)}")

@app.put("/blocks/{block_id}")
async def update_block(block_id: str, request: Dict[str, Any]):
    """Update an existing block"""
    try:
        success = dag_manager.update_block(block_id, request)
        
        if not success:
            raise HTTPException(status_code=404, detail="Block not found")
        
        return {
            "success": True,
            "message": "Block updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating block: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating block: {str(e)}")

@app.delete("/blocks/{block_id}")
async def delete_block(block_id: str):
    """Delete a block"""
    try:
        success = dag_manager.remove_block(block_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Block not found")
        
        return {
            "success": True,
            "message": "Block deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting block: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting block: {str(e)}")

@app.get("/ai/agents")
async def get_ai_agents():
    """Get information about AI agents"""
    try:
        agents_info = []
        for agent_id, agent in agent_manager.agents.items():
            agents_info.append({
                "id": agent_id,
                "name": agent.name,
                "type": agent.agent_type.value,
                "capabilities": [cap.value for cap in agent.capabilities],
                "description": agent.description,
                "model": agent.model,
                "is_active": agent.is_active,
                "last_used": agent.last_used.isoformat() if agent.last_used else None
            })
        
        return {
            "success": True,
            "agents": agents_info,
            "system_status": agent_manager.get_system_status()
        }
        
    except Exception as e:
        logger.error(f"Error getting AI agents: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting AI agents: {str(e)}")

@app.get("/ai/agents/{agent_id}/execute")
async def execute_agent_task(agent_id: str, task: str, context: Dict[str, Any] = None):
    """Execute a task with a specific AI agent"""
    try:
        if agent_id not in agent_manager.agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Execute task
        result = await agent_manager.execute_agent_task(agent_id, task, context or {})
        
        return {
            "success": True,
            "agent_id": agent_id,
            "result": {
                "success": result.success,
                "content": result.content,
                "metadata": result.metadata,
                "error": result.error
            }
        }
        
    except Exception as e:
        logger.error(f"Error executing agent task: {e}")
        raise HTTPException(status_code=500, detail=f"Error executing agent task: {str(e)}")

@app.get("/dag/status")
async def get_dag_status():
    """Get DAG system status"""
    try:
        return {
            "success": True,
            "dag_status": dag_manager.get_system_status(),
            "execution_plan": dag_manager.get_execution_plan(),
            "validation": dag_manager.validate_workflow()
        }
    except Exception as e:
        logger.error(f"Error getting DAG status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting DAG status: {str(e)}")

@app.get("/dag/visualization")
async def get_dag_visualization():
    """Get enhanced DAG visualization data with comprehensive dependency information"""
    try:
        return {
            "success": True,
            "visualization_data": dag_manager.get_dag_visualization_data()
        }
    except Exception as e:
        logger.error(f"Error getting DAG visualization: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting DAG visualization: {str(e)}")

@app.get("/executor/status")
async def get_executor_status():
    """Get Python executor status"""
    try:
        return {
            "success": True,
            "executor_status": python_executor.get_system_status(),
            "sessions": python_executor.list_sessions()
        }
    except Exception as e:
        logger.error(f"Error getting executor status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting executor status: {str(e)}")

@app.get("/system/status")
async def get_system_status():
    """Get overall system status"""
    try:
        return {
            "success": True,
            "status": "running",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {
                "mcp_system": agent_manager.get_system_status(),
                "dag_system": dag_manager.get_system_status(),
                "python_executor": python_executor.get_system_status()
            },
            "metrics": {
                "datasets_count": len(datasets),
                "workflows_count": len(workflows),
                "active_sessions": len(python_executor.session_manager.sessions),
                "total_blocks": dag_manager.graph.number_of_nodes() if dag_manager.graph else 0
            }
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting system status: {str(e)}")

@app.websocket("/ws/workflow/{workflow_id}")
async def workflow_websocket_endpoint(websocket: WebSocket, workflow_id: str):
    """Workflow-specific WebSocket endpoint for real-time updates"""
    await websocket.accept()
    print(f"✅ Workflow WebSocket connected for workflow: {workflow_id}")
    
    try:
        # Subscribe to workflow updates
        await websocket_manager.connect(websocket, workflow_id)
        
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message.get("type") == "get_workflow_status":
                if workflow_id in workflows:
                    workflow = workflows[workflow_id]
                    await websocket.send_text(json.dumps({
                        "type": "workflow_status",
                        "workflow_id": workflow_id,
                        "status": workflow["execution_status"],
                        "blocks_count": len(workflow["blocks"])
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
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metrics": {
                    "datasets_count": len(datasets),
                    "workflows_count": len(workflows),
                    "active_sessions": len(python_executor.session_manager.sessions),
                    "total_blocks": dag_manager.graph.number_of_nodes() if dag_manager.graph else 0
                }
            }
            
            # Broadcast to all connected clients
            for connection in websocket_manager.active_connections:
                try:
                    await connection.send_text(json.dumps(metrics))
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error broadcasting system metrics: {e}")
        
        await asyncio.sleep(10)  # Update every 10 seconds

@app.get("/")
async def root():
    return {
        "message": "Enhanced AI Notebook Backend with MCP Integration", 
        "status": "running",
        "version": "2.0.0",
        "features": [
            "MCP-based AI system",
            "Multi-agent architecture", 
            "Advanced DAG management",
            "Enhanced Python execution",
            "Real-time collaboration"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
