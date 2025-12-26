"""
MCP (Model Context Protocol) based AI Notebook System
Provides powerful AI capabilities through multi-agent architecture
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime, timezone
import re
import traceback

# MCP imports
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.types import (
        TextContent, ImageContent, EmbeddedResource,
        Tool, TextContent, CallToolRequest, CallToolResult
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP not available, falling back to direct Ollama integration")

# Fallback MCP types for when MCP is not available
if not MCP_AVAILABLE:
    class StdioServerParameters:
        def __init__(self, command, args=None):
            self.command = command
            self.args = args or []
    
    class ClientSession:
        def __init__(self, server_params):
            self.server_params = server_params
            self.is_connected = False
        
        async def __aenter__(self):
            self.is_connected = True
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            self.is_connected = False
        
        async def call_tool(self, request):
            return None
    
    # Fallback types
    class CallToolResult:
        def __init__(self, content=None, is_error=False, error=None):
            self.content = content or []
            self.is_error = is_error
            self.error = error
    
    class TextContent:
        def __init__(self, text):
            self.text = text
    
    class Tool:
        def __init__(self, name, description):
            self.name = name
            self.description = description

# Ollama integration
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: Ollama not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of AI agents in the system"""
    PLANNER = "planner"
    EXECUTOR = "executor"
    ANALYZER = "analyzer"
    VISUALIZER = "visualizer"
    DEBUGGER = "debugger"
    OPTIMIZER = "optimizer"

class AgentCapability(Enum):
    """Capabilities that agents can have"""
    CODE_GENERATION = "code_generation"
    CODE_EXECUTION = "code_execution"
    DATA_ANALYSIS = "data_analysis"
    VISUALIZATION = "visualization"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    ERROR_DIAGNOSIS = "error_diagnosis"
    CONTEXT_UNDERSTANDING = "context_understanding"

@dataclass
class Agent:
    """AI Agent with specific capabilities"""
    id: str
    name: str
    agent_type: AgentType
    capabilities: List[AgentCapability]
    model: str
    description: str
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: Optional[datetime] = None
    
    def can_handle(self, capability: AgentCapability) -> bool:
        """Check if agent can handle a specific capability"""
        return capability in self.capabilities

@dataclass
class AgentResponse:
    """Response from an AI agent"""
    agent_id: str
    success: bool
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error: Optional[str] = None

class MCPClient:
    """MCP Client for communicating with AI models"""
    
    def __init__(self, server_params: StdioServerParameters):
        self.server_params = server_params
        self.session: Optional[ClientSession] = None
        self.is_connected = False
        
    async def connect(self):
        """Connect to MCP server"""
        try:
            if MCP_AVAILABLE:
                self.session = ClientSession(self.server_params)
                await self.session.__aenter__()
                self.is_connected = True
                logger.info("Connected to MCP server")
            else:
                logger.warning("MCP not available, using fallback")
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            self.is_connected = False
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.session and self.is_connected:
            try:
                await self.session.__aexit__(None, None, None)
                self.is_connected = False
                logger.info("Disconnected from MCP server")
            except Exception as e:
                logger.error(f"Error disconnecting from MCP server: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[CallToolResult]:
        """Call a tool on the MCP server"""
        if not self.is_connected or not self.session:
            return None
        
        try:
            request = CallToolRequest(
                name=tool_name,
                arguments=arguments
            )
            result = await self.session.call_tool(request)
            return result
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return None

class OllamaClient:
    """Ollama client for local LLM integration"""
    
    def __init__(self, model: str = "qwen2.5:3b"):
        self.model = model
        self.client = None
        self.is_available = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Ollama client"""
        try:
            if OLLAMA_AVAILABLE:
                # Test connection
                models = ollama.list()
                available_models = [m.model for m in models.models]
                
                if self.model not in available_models:
                    logger.warning(f"Model {self.model} not found. Available: {available_models}")
                    if available_models:
                        self.model = available_models[0]
                        logger.info(f"Using model: {self.model}")
                
                self.client = ollama
                self.is_available = True
                logger.info(f"Ollama initialized with model: {self.model}")
            else:
                logger.warning("Ollama not available")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            self.is_available = False
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate response using Ollama"""
        if not self.is_available or not self.client:
            return "Ollama not available"
        
        try:
            # Build full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            # Generate response
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': full_prompt
                }],
                options={
                    'temperature': 0.7,
                    'num_predict': 1000,
                }
            )
            
            return response['message']['content']
        except Exception as e:
            logger.error(f"Error generating Ollama response: {e}")
            return f"Error: {str(e)}"
    
    def _build_prompt(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Build context-aware prompt"""
        if not context:
            return prompt
        
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
        return f"""Context:
{context_str}

User Request:
{prompt}

Please provide a detailed, actionable response based on the context and request."""
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            if self.is_available and self.client:
                models = self.client.list()
                return [m.model for m in models.models]
        except Exception as e:
            logger.error(f"Error getting models: {e}")
        return []

class AgentManager:
    """Manages multiple AI agents and their interactions"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.mcp_client: Optional[MCPClient] = None
        self.ollama_client: Optional[OllamaClient] = None
        self._initialize_agents()
        self._initialize_clients()
    
    def _initialize_agents(self):
        """Initialize the AI agents"""
        agents_data = [
            {
                "id": "planner_001",
                "name": "Workflow Planner",
                "agent_type": AgentType.PLANNER,
                "capabilities": [
                    AgentCapability.CONTEXT_UNDERSTANDING,
                    AgentCapability.WORKFLOW_OPTIMIZATION
                ],
                "model": "qwen2.5:3b",
                "description": "Plans and optimizes notebook workflows"
            },
            {
                "id": "executor_001",
                "name": "Code Executor",
                "agent_type": AgentType.EXECUTOR,
                "capabilities": [
                    AgentCapability.CODE_GENERATION,
                    AgentCapability.CODE_EXECUTION
                ],
                "model": "qwen2.5:3b",
                "description": "Generates and executes Python code"
            },
            {
                "id": "analyzer_001",
                "name": "Data Analyzer",
                "agent_type": AgentType.ANALYZER,
                "capabilities": [
                    AgentCapability.DATA_ANALYSIS,
                    AgentCapability.CONTEXT_UNDERSTANDING
                ],
                "model": "qwen2.5:3b",
                "description": "Analyzes data and provides insights"
            },
            {
                "id": "visualizer_001",
                "name": "Data Visualizer",
                "agent_type": AgentType.VISUALIZER,
                "capabilities": [
                    AgentCapability.VISUALIZATION,
                    AgentCapability.CODE_GENERATION
                ],
                "model": "qwen2.5:3b",
                "description": "Creates data visualizations and charts"
            },
            {
                "id": "debugger_001",
                "name": "Code Debugger",
                "agent_type": AgentType.DEBUGGER,
                "capabilities": [
                    AgentCapability.ERROR_DIAGNOSIS,
                    AgentCapability.CODE_GENERATION
                ],
                "model": "qwen2.5:3b",
                "description": "Diagnoses and fixes code errors"
            },
            {
                "id": "optimizer_001",
                "name": "Workflow Optimizer",
                "agent_type": AgentType.OPTIMIZER,
                "capabilities": [
                    AgentCapability.WORKFLOW_OPTIMIZATION,
                    AgentCapability.CONTEXT_UNDERSTANDING
                ],
                "model": "qwen2.5:3b",
                "description": "Optimizes workflow performance and structure"
            }
        ]
        
        for agent_data in agents_data:
            agent = Agent(**agent_data)
            self.agents[agent.id] = agent
    
    def _initialize_clients(self):
        """Initialize MCP and Ollama clients"""
        # Initialize Ollama client
        self.ollama_client = OllamaClient()
        
        # Initialize MCP client if available
        if MCP_AVAILABLE:
            try:
                # This would be configured based on your MCP server setup
                server_params = StdioServerParameters(
                    command="your-mcp-server-command",
                    args=["--config", "your-config.json"]
                )
                self.mcp_client = MCPClient(server_params)
            except Exception as e:
                logger.warning(f"Could not initialize MCP client: {e}")
    
    def get_agent_by_capability(self, capability: AgentCapability) -> Optional[Agent]:
        """Get an agent that can handle a specific capability"""
        available_agents = [
            agent for agent in self.agents.values()
            if agent.can_handle(capability) and agent.is_active
        ]
        
        if available_agents:
            # Return the most recently used agent, or the first one
            return max(available_agents, key=lambda a: a.last_used or a.created_at)
        return None
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[Agent]:
        """Get all agents of a specific type"""
        return [
            agent for agent in self.agents.values()
            if agent.agent_type == agent_type and agent.is_active
        ]
    
    async def execute_agent_task(
        self,
        agent_id: str,
        task: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Execute a task with a specific agent"""
        if agent_id not in self.agents:
            return AgentResponse(
                agent_id=agent_id,
                success=False,
                content="",
                metadata={},
                error="Agent not found"
            )
        
        agent = self.agents[agent_id]
        agent.last_used = datetime.now(timezone.utc)
        
        try:
            # Try MCP first if available
            if self.mcp_client and self.mcp_client.is_connected:
                # This would use MCP tools
                content = await self._execute_mcp_task(agent, task, context)
            else:
                # Fallback to Ollama
                content = await self.ollama_client.generate_response(task, context)
            
            return AgentResponse(
                agent_id=agent_id,
                success=True,
                content=content,
                metadata={
                    "agent_type": agent.agent_type.value,
                    "capabilities": [c.value for c in agent.capabilities],
                    "model": agent.model
                }
            )
            
        except Exception as e:
            logger.error(f"Error executing task with agent {agent_id}: {e}")
            return AgentResponse(
                agent_id=agent_id,
                success=False,
                content="",
                metadata={},
                error=str(e)
            )
    
    async def _execute_mcp_task(
        self,
        agent: Agent,
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """Execute task using MCP"""
        # This would implement MCP-specific task execution
        # For now, return a placeholder
        return f"MCP task executed by {agent.name}: {task}"
    
    async def collaborative_task_execution(
        self,
        task: str,
        context: Dict[str, Any],
        required_capabilities: List[AgentCapability]
    ) -> List[AgentResponse]:
        """Execute a task using multiple agents collaboratively"""
        responses = []
        
        for capability in required_capabilities:
            agent = self.get_agent_by_capability(capability)
            if agent:
                response = await self.execute_agent_task(
                    agent.id,
                    f"Task: {task}\nRequired capability: {capability.value}",
                    context
                )
                responses.append(response)
        
        return responses
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of the agent system"""
        return {
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.is_active]),
            "agent_types": {t.value: len(self.get_agents_by_type(t)) for t in AgentType},
            "mcp_available": MCP_AVAILABLE,
            "mcp_connected": self.mcp_client.is_connected if self.mcp_client else False,
            "ollama_available": self.ollama_client.is_available if self.ollama_client else False,
            "ollama_model": self.ollama_client.model if self.ollama_client else None,
            "available_models": self.ollama_client.get_available_models() if self.ollama_client else []
        }

class NotebookContext:
    """Maintains context for notebook operations"""
    
    def __init__(self):
        self.workflow_id: Optional[str] = None
        self.dataset_info: Dict[str, Any] = {}
        self.blocks: List[Dict[str, Any]] = []
        self.execution_history: List[Dict[str, Any]] = []
        self.variables: Dict[str, Any] = {}
        self.imports: List[str] = []
        self.errors: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
    
    def update_context(self, **kwargs):
        """Update context with new information"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def add_block(self, block: Dict[str, Any]):
        """Add a block to the context"""
        self.blocks.append(block)
    
    def add_execution_result(self, result: Dict[str, Any]):
        """Add execution result to history"""
        self.execution_history.append(result)
    
    def add_error(self, error: Dict[str, Any]):
        """Add error to context"""
        self.errors.append(error)
    
    def get_context_summary(self) -> str:
        """Get a summary of the current context"""
        summary_parts = []
        
        if self.workflow_id:
            summary_parts.append(f"Workflow ID: {self.workflow_id}")
        
        if self.dataset_info:
            summary_parts.append(f"Dataset: {self.dataset_info.get('name', 'Unknown')}")
            summary_parts.append(f"Rows: {self.dataset_info.get('rows', 0)}")
            summary_parts.append(f"Columns: {len(self.dataset_info.get('columns', []))}")
        
        summary_parts.append(f"Blocks: {len(self.blocks)}")
        summary_parts.append(f"Variables: {len(self.variables)}")
        summary_parts.append(f"Imports: {len(self.imports)}")
        
        if self.errors:
            summary_parts.append(f"Errors: {len(self.errors)}")
        
        return "\n".join(summary_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            "workflow_id": self.workflow_id,
            "dataset_info": self.dataset_info,
            "blocks": self.blocks,
            "execution_history": self.execution_history,
            "variables": self.variables,
            "imports": self.imports,
            "errors": self.errors,
            "metadata": self.metadata
        }

# Global instance
agent_manager = AgentManager()

async def initialize_mcp_system():
    """Initialize the MCP system"""
    if agent_manager.mcp_client:
        await agent_manager.mcp_client.connect()
    logger.info("MCP system initialized")

async def shutdown_mcp_system():
    """Shutdown the MCP system"""
    if agent_manager.mcp_client:
        await agent_manager.mcp_client.disconnect()
    logger.info("MCP system shutdown")
