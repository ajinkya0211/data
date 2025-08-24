from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import structlog

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.block import BlockExecutionRequest
from app.services.ai_provider_service import AIProviderService
from app.services.ai_agent_service import AIAgentService

logger = structlog.get_logger()
router = APIRouter()



@router.post("/chat")
async def chat_with_ai(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Chat with AI agent"""
    try:
        ai_service = AIProviderService()
        
        message = request.get("message", "")
        project_id = request.get("project_id")
        dataset_id = request.get("dataset_id")
        provider = request.get("provider", "ollama")
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message is required"
            )
        
        # Check if this is a notebook control request
        if await _is_notebook_control_request(message):
            return await _handle_notebook_control(message, project_id, current_user, db)
        
        # Regular AI chat
        response = await ai_service.chat_with_ai(
            message=message,
            project_id=project_id,
            dataset_id=dataset_id,
            provider=provider
        )
        
        return {
            "message": message,
            "response": response,
            "provider": provider,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to chat with AI", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to chat with AI"
        )

@router.post("/generate-code")
async def generate_code(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate code using AI"""
    try:
        ai_service = AIProviderService()
        
        prompt = request.get("prompt", "")
        language = request.get("language", "python")
        project_id = request.get("project_id")
        provider = request.get("provider", "ollama")
        
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt is required"
            )
        
        response = await ai_service.generate_code(
            prompt=prompt,
            language=language,
            project_id=project_id,
            provider=provider
        )
        
        return {
            "prompt": prompt,
            "language": language,
            "generated_code": response,
            "provider": provider,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate code", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate code"
        )

@router.post("/notebook-control")
async def notebook_control(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Control notebook using natural language commands"""
    try:
        ai_agent_service = AIAgentService()
        
        command = request.get("command", "")
        project_id = request.get("project_id")
        
        if not command:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Command is required"
            )
        
        if not project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project ID is required"
            )
        
        # Process the natural language command
        result = await ai_agent_service.process_natural_language_request(
            user_request=command,
            project_id=project_id,
            user_id=current_user.id,
            db_session=db
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to execute notebook control", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute notebook control"
        )

@router.get("/notebook-summary/{project_id}")
async def get_notebook_summary(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive notebook summary"""
    try:
        ai_agent_service = AIAgentService()
        
        summary = await ai_agent_service.get_notebook_summary(
            project_id=project_id,
            user_id=current_user.id
        )
        
        return summary
        
    except Exception as e:
        logger.error("Failed to get notebook summary", error=str(e), project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notebook summary"
        )

@router.post("/execute-notebook/{project_id}")
async def execute_notebook(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute all blocks in a notebook"""
    try:
        ai_agent_service = AIAgentService()
        
        result = await ai_agent_service._execute_all_blocks(
            project_id=project_id,
            user_id=current_user.id
        )
        
        return result
        
    except Exception as e:
        logger.error("Failed to execute notebook", error=str(e), project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute notebook"
        )

# Helper functions
async def _is_notebook_control_request(message: str) -> bool:
    """Check if the message is a notebook control request"""
    control_keywords = [
        "import", "load", "read", "open", "clean", "preprocess", "analyze", "calculate",
        "mean", "median", "statistics", "plot", "chart", "visualize", "graph",
        "add", "delete", "edit", "block", "execute", "run", "execute all", "run all"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in control_keywords)

async def _handle_notebook_control(
    message: str, 
    project_id: Optional[str], 
    current_user: User, 
    db: AsyncSession
) -> Dict[str, Any]:
    """Handle notebook control requests"""
    if not project_id:
        return {
            "message": message,
            "response": "I can help you control your notebook! Please specify a project ID to use notebook control features.",
            "type": "notebook_control_help",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    try:
        ai_agent_service = AIAgentService()
        
        # Process the notebook control request
        result = await ai_agent_service.process_natural_language_request(
            user_request=message,
            project_id=project_id,
            user_id=current_user.id,
            db_session=db
        )
        
        if result["success"]:
            response = f"🤖 AI Agent: {result['message']}\n\n"
            response += "Here's what I accomplished:\n"
            
            for action, action_result in result["results"].items():
                if isinstance(action_result, dict) and "message" in action_result:
                    response += f"• {action_result['message']}\n"
            
            response += "\nYou can now view the updated notebook or execute the blocks!"
            
            return {
                "message": message,
                "response": response,
                "type": "notebook_control_success",
                "actions_taken": result["results"],
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "message": message,
                "response": f"🤖 AI Agent: Sorry, I couldn't process that request: {result.get('error', 'Unknown error')}",
                "type": "notebook_control_error",
                "error": result.get("error"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error("Failed to handle notebook control", error=str(e))
        return {
            "message": message,
            "response": f"🤖 AI Agent: I encountered an error while processing your request: {str(e)}",
            "type": "notebook_control_error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Import datetime for timestamp
from datetime import datetime 