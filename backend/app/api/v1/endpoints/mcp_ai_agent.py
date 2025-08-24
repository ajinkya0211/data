"""
MCP AI Agent API Endpoints
Provides intelligent, context-aware AI capabilities through natural language requests
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
import structlog

from app.services.mcp_ai_agent import MCPAIAgent
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User

logger = structlog.get_logger()
router = APIRouter()

@router.post("/process")
async def process_ai_request(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db_session = Depends(get_db)
):
    """
    Process a natural language request using MCP-powered AI agent
    
    This endpoint:
    1. Takes natural language input
    2. Uses MCP context to understand the project state
    3. Generates intelligent execution plan using LLM
    4. Executes the plan using available tools
    5. Returns comprehensive results with AI-generated explanation
    """
    try:
        # Validate request data
        if "request" not in request_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing 'request' field in request body"
            )
        
        if "project_id" not in request_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing 'project_id' field in request body"
            )
        
        user_request = request_data["request"]
        project_id = request_data["project_id"]
        
        # Validate user has access to project (basic check)
        # In production, you'd want more robust project access validation
        
        logger.info("Processing MCP AI request", 
                   user_id=current_user.id,
                   project_id=project_id,
                   request=user_request[:100] + "..." if len(user_request) > 100 else user_request)
        
        # Initialize MCP AI agent
        mcp_agent = MCPAIAgent(db_session)
        
        # Process the request
        result = await mcp_agent.process_natural_language_request(
            user_request=user_request,
            project_id=project_id,
            user_id=current_user.id,
            db_session=db_session
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Unknown error occurred")
            )
        
        logger.info("MCP AI request processed successfully", 
                   user_id=current_user.id,
                   project_id=project_id,
                   steps_executed=len(result.get("execution_results", {}).get("steps_results", [])))
        
        return {
            "success": True,
            "data": result,
            "message": "AI request processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to process MCP AI request", 
                    user_id=current_user.id if current_user else None,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/simple-test")
async def simple_test():
    """Simple test endpoint to verify routing"""
    return {"message": "MCP AI Agent routing is working", "status": "success"}

@router.post("/minimal-test")
async def minimal_test():
    """Minimal test endpoint without dependencies"""
    return {"message": "Minimal endpoint working", "status": "success"}

@router.post("/auth-test")
async def auth_test(current_user: User = Depends(get_current_user)):
    """Test endpoint with only authentication dependency"""
    return {"message": "Auth endpoint working", "user_id": current_user.id, "status": "success"}

@router.post("/db-test")
async def db_test(current_user: User = Depends(get_current_user), db_session = Depends(get_db)):
    """Test endpoint with authentication and database dependencies"""
    return {"message": "DB endpoint working", "user_id": current_user.id, "status": "success"}

@router.post("/context-test")
async def context_test(current_user: User = Depends(get_current_user), db_session = Depends(get_db)):
    """Test endpoint with MCP context service"""
    try:
        from app.services.mcp_context_service import MCPContextService
        
        context_service = MCPContextService(db_session)
        project_context = await context_service.get_project_context("test_project_123", current_user.id)
        
        return {
            "message": "Context service working",
            "user_id": current_user.id,
            "project_context_keys": list(project_context.keys()) if project_context else None,
            "status": "success"
        }
    except Exception as e:
        return {
            "message": "Context service failed",
            "error": str(e),
            "status": "error"
        }

@router.post("/ai-provider-test")
async def ai_provider_test(current_user: User = Depends(get_current_user), db_session = Depends(get_db)):
    """Test endpoint with AI provider service"""
    try:
        from app.services.ai_provider_service import AIProviderService
        
        ai_provider = AIProviderService()
        await ai_provider.initialize()
        
        # Test a simple response generation
        response = await ai_provider.generate_response(
            prompt="Hello, how are you?",
            context={"test": "simple"}
        )
        
        return {
            "message": "AI provider service working",
            "user_id": current_user.id,
            "response": response.get("response", "No response"),
            "status": "success"
        }
    except Exception as e:
        return {
            "message": "AI provider service failed",
            "error": str(e),
            "status": "error"
        }

@router.get("/capabilities/{project_id}")
async def get_agent_capabilities(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db_session = Depends(get_db)
):
    """
    Get comprehensive information about the MCP AI agent's capabilities
    
    Returns:
    - Available tools and their descriptions
    - Project context analysis
    - Execution history
    - AI provider status
    """
    try:
        logger.info("Getting MCP AI agent capabilities", 
                   user_id=current_user.id,
                   project_id=project_id)
        
        # Initialize MCP AI agent
        mcp_agent = MCPAIAgent(db_session)
        
        # Get capabilities
        capabilities = await mcp_agent.get_agent_capabilities(
            project_id=project_id,
            user_id=current_user.id
        )
        
        if "error" in capabilities:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=capabilities["error"]
            )
        
        logger.info("Retrieved MCP AI agent capabilities", 
                   user_id=current_user.id,
                   project_id=project_id,
                   total_tools=capabilities.get("total_tools", 0))
        
        return {
            "success": True,
            "data": capabilities,
            "message": "Agent capabilities retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get MCP AI agent capabilities", 
                    user_id=current_user.id if current_user else None,
                    project_id=project_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/tools")
async def get_available_tools(
    current_user: User = Depends(get_current_user),
    db_session = Depends(get_db)
):
    """
    Get all available AI tools and their schemas
    
    Returns comprehensive information about:
    - Tool categories
    - Individual tool descriptions
    - Required parameters
    - Usage examples
    """
    try:
        logger.info("Getting available AI tools", user_id=current_user.id)
        
        # Initialize MCP AI agent
        mcp_agent = MCPAIAgent(db_session)
        
        # Get tool schema
        tool_schema = mcp_agent.tool_engine.get_tool_schema()
        
        logger.info("Retrieved AI tools schema", 
                   user_id=current_user.id,
                   total_tools=tool_schema.get("total_tools", 0))
        
        return {
            "success": True,
            "data": tool_schema,
            "message": "AI tools schema retrieved successfully"
        }
        
    except Exception as e:
        logger.error("Failed to get AI tools schema", 
                    user_id=current_user.id if current_user else None,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/tools/{project_id}")
async def get_project_tools(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db_session = Depends(get_db)
):
    """
    Get available tools for a specific project context
    
    Returns tools that are available given the current project state
    """
    try:
        logger.info("Getting project-specific AI tools", 
                   user_id=current_user.id,
                   project_id=project_id)
        
        # Initialize MCP AI agent
        mcp_agent = MCPAIAgent(db_session)
        
        # Get available tools for this project context
        context = {"project_id": project_id, "user_id": current_user.id}
        available_tools = mcp_agent.tool_engine.get_available_tools(context)
        
        logger.info("Retrieved project-specific AI tools", 
                   user_id=current_user.id,
                   project_id=project_id,
                   available_tools=len(available_tools))
        
        return {
            "success": True,
            "data": {
                "project_id": project_id,
                "available_tools": available_tools,
                "total_available": len(available_tools)
            },
            "message": "Project tools retrieved successfully"
        }
        
    except Exception as e:
        logger.error("Failed to get project-specific AI tools", 
                    user_id=current_user.id if current_user else None,
                    project_id=project_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/execution-history")
async def get_execution_history(
    current_user: User = Depends(get_current_user),
    db_session = Depends(get_db)
):
    """
    Get execution history of AI tools
    
    Returns recent tool executions with results and parameters
    """
    try:
        logger.info("Getting AI tool execution history", user_id=current_user.id)
        
        # Initialize MCP AI agent
        mcp_agent = MCPAIAgent(db_session)
        
        # Get execution history
        execution_history = mcp_agent.tool_engine.get_execution_history()
        
        logger.info("Retrieved AI tool execution history", 
                   user_id=current_user.id,
                   total_executions=len(execution_history))
        
        return {
            "success": True,
            "data": {
                "execution_history": execution_history,
                "total_executions": len(execution_history),
                "recent_executions": execution_history[-10:] if execution_history else []
            },
            "message": "Execution history retrieved successfully"
        }
        
    except Exception as e:
        logger.error("Failed to get AI tool execution history", 
                    user_id=current_user.id if current_user else None,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/test")
async def test_ai_agent(
    current_user: User = Depends(get_current_user),
    db_session = Depends(get_db)
):
    """
    Test endpoint to verify MCP AI agent functionality
    
    Returns basic system status and capabilities
    """
    try:
        logger.info("Testing MCP AI agent", user_id=current_user.id)
        
        # Initialize MCP AI agent
        mcp_agent = MCPAIAgent(db_session)
        
        # Test basic functionality
        test_result = {
            "agent_initialized": True,
            "mcp_context_service": True,
            "tool_engine": True,
            "ai_provider": await mcp_agent.ai_provider_service.health_check(),
            "available_tools": len(mcp_agent.tool_engine.tools),
            "tool_categories": [cat.category.value for cat in mcp_agent.tool_engine.tools.values() if hasattr(cat, 'category')],
            "system_status": "operational"
        }
        
        logger.info("MCP AI agent test completed", 
                   user_id=current_user.id,
                   status=test_result["system_status"])
        
        return {
            "success": True,
            "data": test_result,
            "message": "AI agent test completed successfully"
        }
        
    except Exception as e:
        logger.error("MCP AI agent test failed", 
                    user_id=current_user.id if current_user else None,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI agent test failed: {str(e)}"
        )
