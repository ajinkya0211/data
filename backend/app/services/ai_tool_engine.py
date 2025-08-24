"""
AI Tool Engine - Tool-based execution for agentic AI
Provides a comprehensive set of tools that AI can use to execute actions
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import structlog
import json
import re

logger = structlog.get_logger()

class ToolCategory(str, Enum):
    DATA_MANIPULATION = "data_manipulation"
    BLOCK_MANAGEMENT = "block_management"
    WORKFLOW_CONTROL = "workflow_control"
    ANALYSIS = "analysis"
    VISUALIZATION = "visualization"
    SYSTEM = "system"

@dataclass
class Tool:
    """Represents an executable tool for the AI agent"""
    name: str
    description: str
    category: ToolCategory
    parameters: Dict[str, Any]
    execute_func: Callable
    examples: List[str]
    required_context: List[str]

class AIToolEngine:
    """
    Engine that provides tools for AI agent execution
    Makes the AI truly agentic by giving it concrete tools to use
    """
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.tools: Dict[str, Tool] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools"""
        # Data manipulation tools
        self._register_tool(
            Tool(
                name="import_dataset",
                description="Import a dataset from various sources (CSV, JSON, etc.)",
                category=ToolCategory.DATA_MANIPULATION,
                parameters={
                    "source_path": "string - Path to the dataset file",
                    "dataset_name": "string - Name for the dataset",
                    "description": "string - Description of the dataset"
                },
                execute_func=self._import_dataset,
                examples=[
                    "import_dataset('data_dirty.csv', 'customer_data', 'Customer transaction data')",
                    "import_dataset('sales.json', 'sales_data', 'Monthly sales information')"
                ],
                required_context=["project_id", "user_id"]
            )
        )
        
        # Block management tools
        self._register_tool(
            Tool(
                name="create_code_block",
                description="Create a new code block with specified content",
                category=ToolCategory.BLOCK_MANAGEMENT,
                parameters={
                    "title": "string - Title of the block",
                    "content": "string - Python code content",
                    "position_x": "integer - X position in the project",
                    "position_y": "integer - Y position in the project"
                },
                execute_func=self._create_code_block,
                examples=[
                    "create_code_block('Data Cleaning', 'df.dropna()', 100, 200)",
                    "create_code_block('Analysis', 'df.describe()', 300, 200)"
                ],
                required_context=["project_id", "user_id"]
            )
        )
        
        # Workflow control tools
        self._register_tool(
            Tool(
                name="execute_workflow",
                description="Execute all blocks in the project as a workflow",
                category=ToolCategory.WORKFLOW_CONTROL,
                parameters={
                    "parallel": "boolean - Whether to execute blocks in parallel where possible"
                },
                execute_func=self._execute_workflow,
                examples=[
                    "execute_workflow(parallel=True)",
                    "execute_workflow(parallel=False)"
                ],
                required_context=["project_id", "user_id"]
            )
        )
        
        # Analysis tools
        self._register_tool(
            Tool(
                name="analyze_dataset",
                description="Perform comprehensive analysis on a dataset",
                category=ToolCategory.ANALYSIS,
                parameters={
                    "dataset_id": "string - ID of the dataset to analyze",
                    "analysis_type": "string - Type of analysis (basic, statistical, quality)"
                },
                execute_func=self._analyze_dataset,
                examples=[
                    "analyze_dataset('dataset_123', 'statistical')",
                    "analyze_dataset('dataset_456', 'quality')"
                ],
                required_context=["project_id", "user_id"]
            )
        )
        
        # Visualization tools
        self._register_tool(
            Tool(
                name="create_visualization",
                description="Create a visualization block for data",
                category=ToolCategory.VISUALIZATION,
                parameters={
                    "chart_type": "string - Type of chart (bar, line, scatter, histogram)",
                    "data_source": "string - Data source for visualization",
                    "title": "string - Title of the visualization"
                },
                execute_func=self._create_visualization,
                examples=[
                    "create_visualization('bar', 'sales_data', 'Monthly Sales')",
                    "create_visualization('scatter', 'customer_data', 'Age vs Income')"
                ],
                required_context=["project_id", "user_id"]
            )
        )
    
    def _register_tool(self, tool: Tool):
        """Register a tool in the engine"""
        self.tools[tool.name] = tool
        logger.info("Registered AI tool", tool_name=tool.name, category=tool.category.value)
    
    def get_available_tools(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get available tools based on current context"""
        available_tools = []
        
        for tool_name, tool in self.tools.items():
            # Check if required context is available
            if all(key in context for key in tool.required_context):
                available_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category.value,
                    "parameters": tool.parameters,
                    "examples": tool.examples
                })
        
        return available_tools
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool with given parameters and context"""
        try:
            if tool_name not in self.tools:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            tool = self.tools[tool_name]
            
            # Validate required context
            missing_context = [key for key in tool.required_context if key not in context]
            if missing_context:
                raise ValueError(f"Missing required context: {missing_context}")
            
            # Execute the tool
            logger.info("Executing AI tool", tool_name=tool_name, parameters=parameters)
            
            result = await tool.execute_func(parameters, context)
            
            # Record execution
            execution_record = {
                "tool_name": tool_name,
                "parameters": parameters,
                "context": context,
                "result": result,
                "timestamp": "2025-08-23T15:30:00Z"
            }
            self.execution_history.append(execution_record)
            
            logger.info("AI tool executed successfully", tool_name=tool_name, result=result)
            
            return {
                "success": True,
                "tool_name": tool_name,
                "result": result,
                "execution_id": len(self.execution_history)
            }
            
        except Exception as e:
            logger.error("Failed to execute AI tool", tool_name=tool_name, error=str(e))
            return {
                "success": False,
                "tool_name": tool_name,
                "error": str(e)
            }
    
    # === TOOL IMPLEMENTATIONS ===
    
    async def _import_dataset(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Import a dataset tool implementation"""
        try:
            from app.services.dataset_service import DatasetService
            
            dataset_service = DatasetService(self.db_session)
            
            # Create dataset
            from app.models.dataset import DatasetCreate
            
            dataset_data = DatasetCreate(
                name=parameters.get("dataset_name", "Imported Dataset"),
                description=parameters.get("description", "Dataset imported via AI tool"),
                source_path=parameters.get("source_path"),
                source_type="file"
            )
            
            dataset = await dataset_service.create_dataset(dataset_data, context["user_id"])
            
            # Profile the dataset
            profile = await dataset_service.profile_dataset(dataset.id)
            
            return {
                "dataset_id": dataset.id,
                "dataset_name": dataset.name,
                "profile_generated": profile is not None,
                "message": f"Successfully imported dataset: {dataset.name}"
            }
            
        except Exception as e:
            logger.error("Failed to import dataset", error=str(e))
            raise
    
    async def _create_code_block(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create code block tool implementation"""
        try:
            from app.services.block_service import BlockService
            
            block_service = BlockService(self.db_session)
            
            from app.models.block import BlockCreate
            
            block_data = BlockCreate(
                project_id=context["project_id"],
                kind="code",
                language="python",
                title=parameters.get("title", "New Code Block"),
                content=parameters.get("content", "# New code block"),
                position_x=parameters.get("position_x", 0),
                position_y=parameters.get("position_y", 0)
            )
            
            block = await block_service.create_block(block_data, context["user_id"])
            
            return {
                "block_id": block.id,
                "block_title": block.title,
                "message": f"Successfully created code block: {block.title}"
            }
            
        except Exception as e:
            logger.error("Failed to create code block", error=str(e))
            raise
    
    async def _execute_workflow(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow tool implementation"""
        try:
            from app.services.workflow_orchestrator import WorkflowOrchestrator
            
            orchestrator = WorkflowOrchestrator(self.db_session)
            
            execution = await orchestrator.execute_project_workflow(
                project_id=context["project_id"],
                user_id=context["user_id"]
            )
            
            return {
                "workflow_id": execution.workflow_id,
                "execution_id": execution.id,
                "status": execution.status.value,
                "total_blocks": len(execution.nodes),
                "message": f"Workflow execution started with {len(execution.nodes)} blocks"
            }
            
        except Exception as e:
            logger.error("Failed to execute workflow", error=str(e))
            raise
    
    async def _analyze_dataset(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dataset tool implementation"""
        try:
            from app.services.dataset_service import DatasetService
            
            dataset_service = DatasetService(self.db_session)
            
            dataset_id = parameters.get("dataset_id")
            analysis_type = parameters.get("analysis_type", "basic")
            
            # Get dataset and profile
            dataset = await dataset_service.get_dataset(dataset_id, context["user_id"])
            profile = await dataset_service.get_latest_profile(dataset_id)
            
            if not profile:
                # Generate profile if it doesn't exist
                profile = await dataset_service.profile_dataset(dataset_id)
            
            analysis_result = {
                "dataset_name": dataset.name,
                "analysis_type": analysis_type,
                "profile_available": profile is not None,
                "basic_stats": profile.statistics if profile else {},
                "schema_info": profile.schema if profile else {}
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error("Failed to analyze dataset", error=str(e))
            raise
    
    async def _create_visualization(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create visualization tool implementation"""
        try:
            from app.services.block_service import BlockService
            
            block_service = BlockService(self.db_session)
            
            chart_type = parameters.get("chart_type", "bar")
            data_source = parameters.get("data_source", "df")
            title = parameters.get("title", f"{chart_type.title()} Chart")
            
            # Generate visualization code based on chart type
            viz_code = self._generate_visualization_code(chart_type, data_source, title)
            
            block_data = {
                "project_id": context["project_id"],
                "kind": "code",
                "language": "python",
                "title": title,
                "content": viz_code,
                "position_x": 400,
                "position_y": 200
            }
            
            block = await block_service.create_block(block_data, context["user_id"])
            
            return {
                "block_id": block.id,
                "chart_type": chart_type,
                "title": title,
                "message": f"Successfully created {chart_type} visualization: {title}"
            }
            
        except Exception as e:
            logger.error("Failed to create visualization", error=str(e))
            raise
    
    def _generate_visualization_code(self, chart_type: str, data_source: str, title: str) -> str:
        """Generate Python code for different chart types"""
        if chart_type == "bar":
            return f'''# {title}
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10, 6))
{data_source}.plot(kind='bar')
plt.title('{title}')
plt.xlabel('Categories')
plt.ylabel('Values')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()'''
        
        elif chart_type == "scatter":
            return f'''# {title}
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10, 6))
plt.scatter({data_source}.iloc[:, 0], {data_source}.iloc[:, 1])
plt.title('{title}')
plt.xlabel('X Axis')
plt.ylabel('Y Axis')
plt.grid(True, alpha=0.3)
plt.show()'''
        
        elif chart_type == "histogram":
            return f'''# {title}
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10, 6))
{data_source}.hist(bins=30, alpha=0.7)
plt.title('{title}')
plt.xlabel('Values')
plt.ylabel('Frequency')
plt.grid(True, alpha=0.3)
plt.show()'''
        
        else:
            return f'''# {title}
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10, 6))
{data_source}.plot()
plt.title('{title}')
plt.xlabel('Index')
plt.ylabel('Values')
plt.grid(True, alpha=0.3)
plt.show()'''
    
    def get_tool_schema(self) -> Dict[str, Any]:
        """Get the complete tool schema for AI consumption"""
        schema = {
            "tools": [],
            "categories": [cat.value for cat in ToolCategory],
            "total_tools": len(self.tools)
        }
        
        for tool_name, tool in self.tools.items():
            schema["tools"].append({
                "name": tool.name,
                "description": tool.description,
                "category": tool.category.value,
                "parameters": tool.parameters,
                "examples": tool.examples,
                "required_context": tool.required_context
            })
        
        return schema
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get the execution history of all tools"""
        return self.execution_history.copy()
