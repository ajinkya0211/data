"""
Workflow API endpoints
Handles workflow creation, execution, and management
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.workflow import (
    WorkflowDefinitionCreate, WorkflowDefinitionUpdate, WorkflowDefinitionResponse,
    WorkflowExecutionRequest, WorkflowExecutionResponse, WorkflowStatusResponse
)
from app.services.workflow_orchestrator import WorkflowOrchestrator
from app.services.workflow_management_service import WorkflowManagementService

logger = structlog.get_logger()
router = APIRouter()

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_project_dependencies(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze project dependencies and create/update workflow definition
    
    This endpoint automatically analyzes all blocks in a project and creates
    a DAG-based workflow definition based on code dependencies.
    """
    try:
        workflow_management = WorkflowManagementService(db)
        
        result = await workflow_management.create_or_update_project_workflow(
            project_id, current_user.id
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )
        
        return {
            "success": True,
            "action": result['action'],
            "workflow_definition": {
                "id": str(result['workflow_definition'].id),
                "name": result['workflow_definition'].name,
                "description": result['workflow_definition'].description,
                "nodes": result['workflow_definition'].nodes,
                "edges": result['workflow_definition'].edges,
                "execution_order": result['workflow_definition'].execution_order,
                "version": result['workflow_definition'].version
            },
            "dag": result['dag'],
            "dependency_analysis": result['dependency_analysis']
        }
        
    except Exception as e:
        logger.error("Project dependency analysis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/project/{project_id}/info", response_model=Dict[str, Any])
async def get_project_workflow_info(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive workflow information for a project"""
    try:
        orchestrator = WorkflowOrchestrator(db)
        
        workflow_info = await orchestrator.get_project_workflow_info(project_id)
        
        return workflow_info
        
    except Exception as e:
        logger.error("Failed to get project workflow info", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow info: {str(e)}"
        )

@router.post("/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    request: WorkflowExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a workflow for a project
    
    This endpoint executes all code blocks in a project as a coordinated workflow,
    with real-time monitoring and dependency resolution.
    """
    try:
        orchestrator = WorkflowOrchestrator(db)
        
        execution = await orchestrator.execute_project_workflow(
            project_id=request.project_id,
            user_id=current_user.id,
            block_ids=None,  # Execute all blocks in workflow
            workflow_definition_id=request.workflow_definition_id
        )
        
        return WorkflowExecutionResponse(
            execution_id=str(execution.id),
            workflow_definition_id=str(execution.workflow_definition_id),
            project_id=execution.project_id,
            status=execution.status,
            current_node=execution.current_node,
            started_at=execution.started_at,
            total_duration=execution.total_duration,
            node_results=execution.node_results,
            node_status=execution.node_status,
            error_message=execution.error_message
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Workflow execution failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}"
        )

@router.get("/status/{execution_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the current status of a workflow execution"""
    try:
        orchestrator = WorkflowOrchestrator(db)
        execution = await orchestrator.get_workflow_status(execution_id)
        
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow execution not found"
            )
        
        # Calculate statistics
        node_status = execution.node_status or {}
        total_nodes = len(execution.workflow_definition.nodes)
        completed_nodes = len([
            status for status in node_status.values() 
            if status == "completed"
        ])
        failed_nodes = len([
            status for status in node_status.values() 
            if status == "failed"
        ])
        
        return WorkflowStatusResponse(
            execution_id=str(execution.id),
            workflow_definition_id=str(execution.workflow_definition_id),
            project_id=execution.project_id,
            status=execution.status,
            current_node=execution.current_node,
            started_at=execution.started_at,
            completed_at=execution.completed_at,
            total_duration=execution.total_duration,
            total_nodes=total_nodes,
            completed_nodes=completed_nodes,
            failed_nodes=failed_nodes,
            error_message=execution.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get workflow status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow status: {str(e)}"
        )

@router.delete("/cancel/{execution_id}")
async def cancel_workflow(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a running workflow execution"""
    try:
        orchestrator = WorkflowOrchestrator(db)
        
        success = await orchestrator.cancel_workflow(execution_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel workflow execution"
            )
        
        return {"success": True, "message": "Workflow cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to cancel workflow", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel workflow: {str(e)}"
        )

@router.get("/project/{project_id}/executions", response_model=List[Dict[str, Any]])
async def list_project_executions(
    project_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List workflow executions for a project"""
    try:
        workflow_management = WorkflowManagementService(db)
        
        executions = await workflow_management.list_project_executions(project_id, limit)
        
        return [
            {
                "id": str(exec.id),
                "workflow_definition_id": str(exec.workflow_definition_id),
                "status": exec.status,
                "started_at": exec.started_at.isoformat() if exec.started_at else None,
                "completed_at": exec.completed_at.isoformat() if exec.completed_at else None,
                "current_node": exec.current_node,
                "error_message": exec.error_message,
                "created_at": exec.created_at.isoformat()
            }
            for exec in executions
        ]
        
    except Exception as e:
        logger.error("Failed to list project executions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list executions: {str(e)}"
        )

@router.get("/project/{project_id}/statistics", response_model=Dict[str, Any])
async def get_project_execution_statistics(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get execution statistics for a project"""
    try:
        workflow_management = WorkflowManagementService(db)
        
        statistics = await workflow_management.get_execution_statistics(project_id)
        
        return statistics
        
    except Exception as e:
        logger.error("Failed to get execution statistics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )

@router.get("/definitions/{workflow_id}", response_model=WorkflowDefinitionResponse)
async def get_workflow_definition(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific workflow definition"""
    try:
        workflow_management = WorkflowManagementService(db)
        
        workflow = await workflow_management.get_workflow_definition(workflow_id)
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow definition not found"
            )
        
        return WorkflowDefinitionResponse(
            id=str(workflow.id),
            project_id=str(workflow.project_id),
            name=workflow.name,
            description=workflow.description,
            nodes=workflow.nodes,
            edges=workflow.edges,
            execution_order=workflow.execution_order,
            dependency_map=workflow.dependency_map,
            is_active=workflow.is_active,
            version=workflow.version,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get workflow definition", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow definition: {str(e)}"
        )

@router.put("/definitions/{workflow_id}", response_model=WorkflowDefinitionResponse)
async def update_workflow_definition(
    workflow_id: str,
    update_data: WorkflowDefinitionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a workflow definition"""
    try:
        workflow_management = WorkflowManagementService(db)
        
        workflow = await workflow_management.update_workflow_definition(
            workflow_id, update_data
        )
        
        return WorkflowDefinitionResponse(
            id=str(workflow.id),
            project_id=str(workflow.project_id),
            name=workflow.name,
            description=workflow.description,
            nodes=workflow.nodes,
            edges=workflow.edges,
            execution_order=workflow.execution_order,
            dependency_map=workflow.dependency_map,
            is_active=workflow.is_active,
            version=workflow.version,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to update workflow definition", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workflow definition: {str(e)}"
        )
