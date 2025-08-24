"""
MCP-Powered AI Agent - Revolutionary AI with Context Awareness and Tool Execution
Replaces rule-based system with LLM-powered intelligent decision making
"""

import asyncio
import json
import re
from typing import Dict, Any, List, Optional, Tuple
import structlog
from datetime import datetime
import uuid

from app.services.mcp_context_service import MCPContextService
from app.services.ai_tool_engine import AIToolEngine
from app.services.ai_provider_service import AIProviderService

logger = structlog.get_logger()

class MCPAIAgent:
    """
    Revolutionary MCP-powered AI agent with:
    - Context-aware decision making
    - LLM-powered natural language understanding
    - Tool-based execution capabilities
    - Intelligent workflow generation
    """
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.mcp_context_service = MCPContextService(db_session)
        self.tool_engine = AIToolEngine(db_session)
        self.ai_provider_service = AIProviderService()
    
    async def _initialize_ai_provider(self):
        """Initialize the AI provider service"""
        try:
            await self.ai_provider_service.initialize()
            logger.info("AI provider initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize AI provider", error=str(e))
    
    async def process_natural_language_request(
        self, 
        user_request: str, 
        project_id: str, 
        user_id: str,
        db_session
    ) -> Dict[str, Any]:
        """
        Process natural language request using MCP context and LLM intelligence
        
        This is the main entry point that:
        1. Gathers rich context using MCP
        2. Uses LLM to understand the request and plan actions
        3. Executes tools based on the plan
        4. Returns comprehensive results
        """
        try:
            logger.info("Processing MCP AI request", 
                       request=user_request, 
                       project_id=project_id, 
                       user_id=user_id)
            
            # Initialize AI provider if needed
            await self._initialize_ai_provider()
            
            # Step 1: Gather rich context using MCP
            project_context = await self.mcp_context_service.get_project_context(project_id, user_id)
            
            # Step 2: Use LLM to understand request and plan actions
            ai_plan = await self._generate_ai_plan(user_request, project_context, user_id)
            
            # Step 3: Execute the planned actions using tools
            execution_results = await self._execute_ai_plan(ai_plan, project_id, user_id)
            
            # Step 4: Generate intelligent response
            ai_response = await self._generate_ai_response(user_request, execution_results, project_context)
            
            return {
                "success": True,
                "request": user_request,
                "ai_plan": ai_plan,
                "execution_results": execution_results,
                "ai_response": ai_response,
                "context_used": {
                    "project_context_size": len(str(project_context)),
                    "tools_available": len(self.tool_engine.get_available_tools({"project_id": project_id, "user_id": user_id})),
                    "context_generated_at": datetime.utcnow().isoformat()
                },
                "message": "MCP AI agent successfully processed your request"
            }
            
        except Exception as e:
            logger.error("Failed to process MCP AI request", 
                        error=str(e), 
                        request=user_request,
                        project_id=project_id)
            return {
                "success": False,
                "request": user_request,
                "error": str(e),
                "message": f"MCP AI agent failed to process request: {str(e)}"
            }
    
    async def _generate_ai_plan(
        self, 
        user_request: str, 
        project_context: Dict[str, Any], 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Use LLM to generate an intelligent execution plan
        
        The LLM analyzes the request in context and creates a structured plan
        """
        try:
            # Get available tools for this context
            available_tools = self.tool_engine.get_available_tools({
                "project_id": project_context["project"]["id"],
                "user_id": user_id
            })
            
            # Create comprehensive prompt for LLM
            prompt = self._build_planning_prompt(user_request, project_context, available_tools)
            
            # Get LLM response
            llm_response = await self.ai_provider_service.generate_response(
                prompt=prompt,
                context={
                    "user_request": user_request,
                    "project_context": project_context,
                    "available_tools": available_tools
                }
            )
            
            # Parse LLM response into structured plan
            ai_plan = self._parse_llm_plan(llm_response.get("response", ""), available_tools)
            
            logger.info("Generated AI plan", 
                       plan_steps=len(ai_plan.get("steps", [])),
                       tools_to_use=len(ai_plan.get("tools_to_use", [])))
            
            return ai_plan
            
        except Exception as e:
            logger.error("Failed to generate AI plan", error=str(e))
            # Fallback to basic plan
            return self._generate_fallback_plan(user_request, project_context)
    
    def _build_planning_prompt(
        self, 
        user_request: str, 
        project_context: Dict[str, Any], 
        available_tools: List[Dict[str, Any]]
    ) -> str:
        """Build comprehensive prompt for LLM planning"""
        
        prompt = f"""
You are an intelligent AI agent for a data science workflow platform. Your task is to understand the user's request and create a detailed execution plan.

USER REQUEST: {user_request}

PROJECT CONTEXT:
- Project: {project_context['project']['name']} ({project_context['project']['description']})
- Current blocks: {project_context['blocks']['total']} blocks
- Block types: {json.dumps(project_context['blocks']['by_type'])}
- Data insights: {len(project_context['data']['datasets'])} datasets available
- User expertise: {project_context['user']['expertise_level']}

AVAILABLE TOOLS:
{json.dumps(available_tools, indent=2)}

TASK: Analyze the user request and create a detailed execution plan that:
1. Understands what the user wants to accomplish
2. Identifies which tools to use and in what order
3. Considers the current project state and data
4. Provides specific parameters for each tool
5. Handles any data dependencies or prerequisites

RESPONSE FORMAT (JSON):
{{
    "understanding": "Brief explanation of what the user wants",
    "plan_summary": "High-level plan description",
    "steps": [
        {{
            "step_number": 1,
            "description": "What this step accomplishes",
            "tool_name": "name_of_tool_to_use",
            "parameters": {{"param1": "value1", "param2": "value2"}},
            "reasoning": "Why this step is needed"
        }}
    ],
    "tools_to_use": ["list", "of", "tool", "names"],
    "estimated_complexity": "low|medium|high",
    "potential_issues": ["list", "of", "potential", "problems"],
    "success_criteria": "How to know if the request was successful"
}}

Think step by step and be specific about tool parameters and execution order.
"""
        
        return prompt
    
    def _parse_llm_plan(self, llm_response: str, available_tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse LLM response into structured execution plan"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                
                # Validate and clean the plan
                validated_plan = self._validate_plan(plan, available_tools)
                return validated_plan
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to parse LLM plan as JSON", error=str(e))
        
        # Fallback: create basic plan from text
        return self._create_basic_plan_from_text(llm_response, available_tools)
    
    def _validate_plan(self, plan: Dict[str, Any], available_tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate and clean the LLM-generated plan"""
        available_tool_names = [tool["name"] for tool in available_tools]
        
        # Ensure required fields exist
        required_fields = ["understanding", "plan_summary", "steps"]
        for field in required_fields:
            if field not in plan:
                plan[field] = "Not specified"
        
        # Validate steps
        if "steps" in plan and isinstance(plan["steps"], list):
            validated_steps = []
            for step in plan["steps"]:
                if isinstance(step, dict):
                    # Ensure tool exists
                    tool_name = step.get("tool_name", "")
                    if tool_name in available_tool_names:
                        validated_steps.append(step)
                    else:
                        logger.warning(f"Tool {tool_name} not available, skipping step")
            
            plan["steps"] = validated_steps
        
        # Ensure tools_to_use is a list
        if "tools_to_use" not in plan or not isinstance(plan["tools_to_use"], list):
            plan["tools_to_use"] = []
        
        return plan
    
    def _create_basic_plan_from_text(self, text: str, available_tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create basic plan when LLM response parsing fails"""
        # Simple keyword-based plan generation
        text_lower = text.lower()
        
        steps = []
        tools_to_use = []
        
        # Detect common patterns
        if any(word in text_lower for word in ["import", "load", "read"]):
            if "import_dataset" in [tool["name"] for tool in available_tools]:
                steps.append({
                    "step_number": 1,
                    "description": "Import the dataset",
                    "tool_name": "import_dataset",
                    "parameters": {"source_path": "s3://notebook-artifacts/datasets/data_dirty.csv", "dataset_name": "data_dirty", "description": "Dataset imported via AI tool"},
                    "reasoning": "Need to import data before processing"
                })
                tools_to_use.append("import_dataset")
        
        if any(word in text_lower for word in ["clean", "preprocess", "handle missing"]):
            if "create_code_block" in [tool["name"] for tool in available_tools]:
                steps.append({
                    "step_number": len(steps) + 1,
                    "description": "Create data cleaning block",
                    "tool_name": "create_code_block",
                    "parameters": {"title": "Data Cleaning", "content": "# Data cleaning code"},
                    "reasoning": "Need to clean the data"
                })
                tools_to_use.append("create_code_block")
        
        return {
            "understanding": "Basic plan based on keyword analysis",
            "plan_summary": f"Execute {len(steps)} steps based on detected requirements",
            "steps": steps,
            "tools_to_use": tools_to_use,
            "estimated_complexity": "low",
            "potential_issues": ["Limited understanding due to parsing failure"],
            "success_criteria": "All planned steps complete successfully"
        }
    
    def _generate_fallback_plan(self, user_request: str, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback plan when LLM planning fails"""
        return {
            "understanding": "Fallback plan due to AI planning failure",
            "plan_summary": "Basic execution using available tools",
            "steps": [
                {
                    "step_number": 1,
                    "description": "Import the dataset",
                    "tool_name": "import_dataset",
                    "parameters": {"source_path": "s3://notebook-artifacts/datasets/data_dirty.csv", "dataset_name": "data_dirty", "description": "Dataset imported via AI tool"},
                    "reasoning": "Need to import data before processing"
                },
                {
                    "step_number": 2,
                    "description": "Create data cleaning code block",
                    "tool_name": "create_code_block",
                    "parameters": {"title": "Data Cleaning", "content": "# Data cleaning code\nimport pandas as pd\n\n# Load the dataset\ndf = pd.read_csv('data_dirty.csv')\n\n# Basic cleaning\nprint('Dataset shape:', df.shape)\nprint('Columns:', df.columns.tolist())\nprint('Missing values:', df.isnull().sum())"},
                    "reasoning": "Create code block for data cleaning workflow"
                },
                {
                    "step_number": 3,
                    "description": "Create visualization block",
                    "tool_name": "create_code_block",
                    "parameters": {"title": "Data Visualization", "content": "# Data visualization code\nimport matplotlib.pyplot as plt\nimport seaborn as sns\n\n# Create visualizations\nplt.figure(figsize=(12, 8))\n\n# Example: Distribution plot\nplt.subplot(2, 2, 1)\nplt.hist(df.iloc[:, 0].dropna(), bins=20)\nplt.title('Distribution of first column')\n\nplt.tight_layout()\nplt.show()"},
                    "reasoning": "Create visualization block for data analysis"
                }
            ],
            "tools_to_use": ["import_dataset", "create_code_block"],
            "estimated_complexity": "medium",
            "potential_issues": ["Limited intelligence due to fallback mode"],
            "success_criteria": "Dataset imported and basic blocks created successfully"
        }
    
    async def _execute_ai_plan(
        self, 
        ai_plan: Dict[str, Any], 
        project_id: str, 
        user_id: str
    ) -> Dict[str, Any]:
        """Execute the AI-generated plan using available tools"""
        try:
            execution_results = {
                "plan_executed": ai_plan,
                "steps_results": [],
                "overall_success": True,
                "execution_summary": ""
            }
            
            context = {"project_id": project_id, "user_id": user_id}
            
            # Execute each step in the plan
            for step in ai_plan.get("steps", []):
                try:
                    step_result = await self._execute_plan_step(step, context)
                    execution_results["steps_results"].append(step_result)
                    
                    if not step_result.get("success", False):
                        execution_results["overall_success"] = False
                    
                except Exception as e:
                    step_result = {
                        "step_number": step.get("step_number", 0),
                        "success": False,
                        "error": str(e),
                        "tool_name": step.get("tool_name", "unknown")
                    }
                    execution_results["steps_results"].append(step_result)
                    execution_results["overall_success"] = False
            
            # Generate execution summary
            execution_results["execution_summary"] = self._generate_execution_summary(execution_results)
            
            logger.info("AI plan execution completed", 
                       total_steps=len(execution_results["steps_results"]),
                       success_rate=sum(1 for r in execution_results["steps_results"] if r.get("success", False)) / len(execution_results["steps_results"]) if execution_results["steps_results"] else 0)
            
            return execution_results
            
        except Exception as e:
            logger.error("Failed to execute AI plan", error=str(e))
            return {
                "plan_executed": ai_plan,
                "steps_results": [],
                "overall_success": False,
                "execution_summary": f"Execution failed: {str(e)}",
                "error": str(e)
            }
    
    async def _execute_plan_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step from the AI plan"""
        try:
            tool_name = step.get("tool_name")
            parameters = step.get("parameters", {})
            
            if not tool_name:
                return {
                    "step_number": step.get("step_number", 0),
                    "success": False,
                    "error": "No tool name specified"
                }
            
            # Execute the tool
            tool_result = await self.tool_engine.execute_tool(tool_name, parameters, context)
            
            return {
                "step_number": step.get("step_number", 0),
                "tool_name": tool_name,
                "parameters": parameters,
                "success": tool_result.get("success", False),
                "result": tool_result.get("result", {}),
                "error": tool_result.get("error"),
                "description": step.get("description", "")
            }
            
        except Exception as e:
            logger.error("Failed to execute plan step", step=step, error=str(e))
            return {
                "step_number": step.get("step_number", 0),
                "success": False,
                "error": str(e),
                "tool_name": step.get("tool_name", "unknown")
            }
    
    def _generate_execution_summary(self, execution_results: Dict[str, Any]) -> str:
        """Generate human-readable execution summary"""
        total_steps = len(execution_results["steps_results"])
        successful_steps = sum(1 for r in execution_results["steps_results"] if r.get("success", False))
        
        if total_steps == 0:
            return "No steps were executed"
        
        success_rate = (successful_steps / total_steps) * 100
        
        summary = f"Executed {total_steps} steps with {success_rate:.1f}% success rate. "
        
        if successful_steps == total_steps:
            summary += "All steps completed successfully!"
        elif successful_steps > 0:
            summary += f"{successful_steps} steps succeeded, {total_steps - successful_steps} failed."
        else:
            summary += "All steps failed."
        
        return summary
    
    async def _generate_ai_response(
        self, 
        user_request: str, 
        execution_results: Dict[str, Any], 
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate intelligent response based on execution results"""
        try:
            # Create response prompt
            response_prompt = self._build_response_prompt(user_request, execution_results, project_context)
            
            # Get LLM response
            llm_response = await self.ai_provider_service.generate_response(
                prompt=response_prompt,
                context={
                    "user_request": user_request,
                    "execution_results": execution_results,
                    "project_context": project_context
                }
            )
            
            # Parse and structure the response
            ai_response = self._parse_ai_response(llm_response.get("response", ""), execution_results)
            
            return ai_response
            
        except Exception as e:
            logger.error("Failed to generate AI response", error=str(e))
            # Fallback response
            return self._generate_fallback_response(execution_results)
    
    def _build_response_prompt(
        self, 
        user_request: str, 
        execution_results: Dict[str, Any], 
        project_context: Dict[str, Any]
    ) -> str:
        """Build prompt for AI response generation"""
        
        prompt = f"""
You are an intelligent AI assistant. The user made a request and you executed a plan to fulfill it. Now provide a helpful, informative response.

USER REQUEST: {user_request}

EXECUTION RESULTS:
{json.dumps(execution_results, indent=2)}

PROJECT CONTEXT:
- Project: {project_context['project']['name']}
- Current state: {project_context['blocks']['total']} blocks
- Data available: {len(project_context['data']['datasets'])} datasets

TASK: Provide a helpful response that:
1. Acknowledges what was accomplished
2. Explains what was done step by step
3. Highlights any issues or limitations
4. Suggests next steps or improvements
5. Uses a friendly, helpful tone

RESPONSE FORMAT (JSON):
{{
    "summary": "Brief summary of what was accomplished",
    "detailed_explanation": "Step-by-step explanation of what was done",
    "success_indicators": ["list", "of", "what", "worked", "well"],
    "issues_or_limitations": ["list", "of", "any", "problems", "encountered"],
    "next_steps": ["suggested", "next", "actions"],
    "improvements": ["ways", "to", "enhance", "the", "workflow"],
    "user_message": "Friendly message to the user"
}}

Be specific about what was created, modified, or executed. If there were failures, explain what went wrong and how to fix it.
"""
        
        return prompt
    
    def _parse_ai_response(self, llm_response: str, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured AI response"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                response = json.loads(json_match.group())
                
                # Ensure required fields exist
                required_fields = ["summary", "detailed_explanation", "user_message"]
                for field in required_fields:
                    if field not in response:
                        response[field] = "Not specified"
                
                return response
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to parse AI response as JSON", error=str(e))
        
        # Fallback: create basic response
        return self._create_basic_response_from_text(llm_response, execution_results)
    
    def _create_basic_response_from_text(self, text: str, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create basic response when LLM response parsing fails"""
        return {
            "summary": "Request processed using AI tools",
            "detailed_explanation": text[:500] + "..." if len(text) > 500 else text,
            "success_indicators": ["AI tools executed successfully"],
            "issues_or_limitations": ["Limited response generation due to parsing failure"],
            "next_steps": ["Review the created blocks and execute if needed"],
            "improvements": ["Consider refining the request for better results"],
            "user_message": "I've processed your request using available tools. Check the results above for details."
        }
    
    def _generate_fallback_response(self, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback response when AI response generation fails"""
        return {
            "summary": "Request processed with basic tools",
            "detailed_explanation": "The system executed your request using available tools but couldn't generate a detailed explanation.",
            "success_indicators": ["Tools executed successfully"],
            "issues_or_limitations": ["AI response generation failed"],
            "next_steps": ["Review the execution results above"],
            "improvements": ["Check system logs for more details"],
            "user_message": "Your request has been processed. Please review the results above."
        }
    
    async def get_agent_capabilities(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Get comprehensive information about agent capabilities"""
        try:
            # Get project context
            project_context = await self.mcp_context_service.get_project_context(project_id, user_id)
            
            # Get available tools
            available_tools = self.tool_engine.get_available_tools({
                "project_id": project_id,
                "user_id": user_id
            })
            
            # Get tool schema
            tool_schema = self.tool_engine.get_tool_schema()
            
            # Get execution history
            execution_history = self.tool_engine.get_execution_history()
            
            return {
                "agent_type": "MCP-Powered AI Agent",
                "capabilities": {
                    "context_awareness": True,
                    "llm_powered_planning": True,
                    "tool_based_execution": True,
                    "intelligent_workflow_generation": True,
                    "real_time_monitoring": True
                },
                "available_tools": available_tools,
                "tool_categories": tool_schema["categories"],
                "total_tools": len(available_tools),
                "project_context": {
                    "context_size": len(str(project_context)),
                    "blocks_analyzed": project_context["blocks"]["total"],
                    "data_insights": len(project_context["data"]["datasets"])
                },
                "execution_history": {
                    "total_executions": len(execution_history),
                    "recent_executions": execution_history[-5:] if execution_history else []
                },
                "ai_provider_status": await self.ai_provider_service.health_check()
            }
            
        except Exception as e:
            logger.error("Failed to get agent capabilities", error=str(e))
            return {
                "agent_type": "MCP-Powered AI Agent",
                "error": str(e),
                "capabilities": {}
            }
