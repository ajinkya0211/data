"""
Workflow Management Service
Manages workflow definitions, DAG creation, and execution tracking
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.workflow import (
    WorkflowDefinition, WorkflowExecution, 
    WorkflowDefinitionCreate, WorkflowDefinitionUpdate
)
from app.services.dag_analyzer_service import DAGAnalyzerService
from app.services.block_service import BlockService

logger = structlog.get_logger()

class WorkflowManagementService:
    """Service for managing workflow definitions and executions"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.dag_analyzer = DAGAnalyzerService(db_session)
        self.block_service = BlockService(db_session)
    
    async def create_or_update_project_workflow(self, project_id: str, 
                                             user_id: str) -> Dict[str, Any]:
        """
        Automatically create or update workflow definition for a project
        
        Args:
            project_id: Project to analyze
            user_id: User requesting the workflow
            
        Returns:
            Dict with workflow definition information
        """
        try:
            logger.info("Creating/updating project workflow", project_id=project_id)
            
            # Analyze project dependencies
            analysis_result = await self.dag_analyzer.analyze_project_dependencies(project_id)
            
            if not analysis_result['is_valid']:
                return {
                    "success": False,
                    "error": analysis_result['error'],
                    "workflow_definition": None
                }
            
            # Build DAG from dependencies
            dag = analysis_result['dag']
            
            # Convert dependency map to JSON-serializable format
            dependency_map_dict = {}
            if analysis_result.get('dependency_map'):
                for block_id, deps in analysis_result['dependency_map'].items():
                    if hasattr(deps, 'to_dict'):
                        dependency_map_dict[block_id] = deps.to_dict()
                    else:
                        dependency_map_dict[block_id] = deps
            
            # Check if workflow definition already exists
            existing_workflow = await self.get_project_workflow(project_id)
            
            if existing_workflow:
                # Update existing workflow
                workflow = await self.update_workflow_definition(
                    existing_workflow.id,
                    WorkflowDefinitionUpdate(
                        nodes=dag['nodes'],
                        edges=dag['edges'],
                        execution_order=dag['execution_order'],
                        dependency_map=dependency_map_dict
                    )
                )
                action = "updated"
            else:
                # Create new workflow definition
                workflow = await self.create_workflow_definition(
                    WorkflowDefinitionCreate(
                        project_id=project_id,
                        name=f"Auto-generated workflow for project {project_id}",
                        description="Automatically generated workflow based on code analysis",
                        nodes=dag['nodes'],
                        edges=dag['edges'],
                        execution_order=dag['execution_order'],
                        dependency_map=dependency_map_dict
                    )
                )
                action = "created"
            
            logger.info("Project workflow successfully created/updated", 
                       project_id=project_id, action=action, workflow_id=workflow.id)
            
            return {
                "success": True,
                "action": action,
                "workflow_definition": workflow,
                "dag": dag,
                "dependency_analysis": analysis_result
            }
            
        except Exception as e:
            logger.error("Failed to create/update project workflow", 
                        project_id=project_id, error=str(e))
            return {
                "success": False,
                "error": f"Workflow creation failed: {str(e)}",
                "workflow_definition": None
            }
    
    async def create_workflow_definition(self, 
                                       workflow_data: WorkflowDefinitionCreate) -> WorkflowDefinition:
        """Create a new workflow definition"""
        
        workflow = WorkflowDefinition(
            project_id=workflow_data.project_id,
            name=workflow_data.name,
            description=workflow_data.description,
            nodes=workflow_data.nodes,
            edges=workflow_data.edges,
            execution_order=workflow_data.execution_order,
            dependency_map=workflow_data.dependency_map
        )
        
        self.db_session.add(workflow)
        await self.db_session.commit()
        await self.db_session.refresh(workflow)
        
        return workflow
    
    async def update_workflow_definition(self, workflow_id: str, 
                                       update_data: WorkflowDefinitionUpdate) -> WorkflowDefinition:
        """Update an existing workflow definition"""
        
        # Get current workflow
        workflow = await self.get_workflow_definition(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow definition {workflow_id} not found")
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        update_dict['updated_at'] = datetime.utcnow()
        
        await self.db_session.execute(
            update(WorkflowDefinition)
            .where(WorkflowDefinition.id == workflow_id)
            .values(**update_dict)
        )
        
        await self.db_session.commit()
        
        # Return updated workflow
        return await self.get_workflow_definition(workflow_id)
    
    async def get_workflow_definition(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get workflow definition by ID"""
        
        result = await self.db_session.execute(
            select(WorkflowDefinition)
            .where(WorkflowDefinition.id == workflow_id)
        )
        
        return result.scalar_one_or_none()
    
    async def get_project_workflow(self, project_id: str) -> Optional[WorkflowDefinition]:
        """Get active workflow definition for a project"""
        
        result = await self.db_session.execute(
            select(WorkflowDefinition)
            .where(WorkflowDefinition.project_id == project_id)
            .where(WorkflowDefinition.is_active == True)
            .order_by(WorkflowDefinition.updated_at.desc())
        )
        
        return result.scalar_one_or_none()
    
    async def list_project_workflows(self, project_id: str) -> List[WorkflowDefinition]:
        """List all workflow definitions for a project"""
        
        result = await self.db_session.execute(
            select(WorkflowDefinition)
            .where(WorkflowDefinition.project_id == project_id)
            .order_by(WorkflowDefinition.created_at.desc())
        )
        
        return result.scalars().all()
    
    async def create_workflow_execution(self, workflow_definition_id: str, 
                                      project_id: str, user_id: str,
                                      session_id: Optional[str] = None) -> WorkflowExecution:
        """Create a new workflow execution instance"""
        
        execution = WorkflowExecution(
            workflow_definition_id=workflow_definition_id,
            project_id=project_id,
            user_id=user_id,
            session_id=session_id,
            status="pending"
        )
        
        self.db_session.add(execution)
        await self.db_session.commit()
        await self.db_session.refresh(execution)
        
        return execution
    
    async def update_execution_status(self, execution_id: str, 
                                    status: str, 
                                    current_node: Optional[str] = None,
                                    node_results: Optional[Dict[str, Any]] = None,
                                    node_status: Optional[Dict[str, str]] = None,
                                    error_message: Optional[str] = None,
                                    session_id: Optional[str] = None) -> WorkflowExecution:
        """Update workflow execution status"""
        
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if current_node is not None:
            update_data["current_node"] = current_node
        
        if node_results is not None:
            update_data["node_results"] = node_results
        
        if node_status is not None:
            update_data["node_status"] = node_status
        
        if error_message is not None:
            update_data["error_message"] = error_message
        
        if session_id is not None:
            update_data["session_id"] = session_id
        
        if status == "running" and not update_data.get("started_at"):
            update_data["started_at"] = datetime.utcnow()
        
        if status in ["completed", "failed", "cancelled"]:
            update_data["completed_at"] = datetime.utcnow()
        
        await self.db_session.execute(
            update(WorkflowExecution)
            .where(WorkflowExecution.id == execution_id)
            .values(**update_data)
        )
        
        await self.db_session.commit()
        
        # Return updated execution
        result = await self.db_session.execute(
            select(WorkflowExecution)
            .where(WorkflowExecution.id == execution_id)
        )
        
        return result.scalar_one_or_none()
    
    async def get_workflow_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution by ID"""
        
        result = await self.db_session.execute(
            select(WorkflowExecution)
            .options(selectinload(WorkflowExecution.workflow_definition))
            .where(WorkflowExecution.id == execution_id)
        )
        
        return result.scalar_one_or_none()
    
    async def list_project_executions(self, project_id: str, 
                                    limit: int = 50) -> List[WorkflowExecution]:
        """List workflow executions for a project"""
        
        result = await self.db_session.execute(
            select(WorkflowExecution)
            .options(selectinload(WorkflowExecution.workflow_definition))
            .where(WorkflowExecution.project_id == project_id)
            .order_by(WorkflowExecution.created_at.desc())
            .limit(limit)
        )
        
        return result.scalars().all()
    
    async def cancel_workflow_execution(self, execution_id: str) -> bool:
        """Cancel a running workflow execution"""
        
        execution = await self.get_workflow_execution(execution_id)
        if not execution:
            return False
        
        if execution.status not in ["pending", "running"]:
            return False
        
        await self.update_execution_status(
            execution_id, 
            "cancelled",
            error_message="Execution cancelled by user"
        )
        
        return True
    
    async def get_execution_statistics(self, project_id: str) -> Dict[str, Any]:
        """Get workflow execution statistics for a project"""
        
        # Get all executions for the project
        executions = await self.list_project_executions(project_id, limit=1000)
        
        if not executions:
            return {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "cancelled_executions": 0,
                "average_duration": 0,
                "success_rate": 0.0
            }
        
        # Calculate statistics
        total = len(executions)
        successful = len([e for e in executions if e.status == "completed"])
        failed = len([e for e in executions if e.status == "failed"])
        cancelled = len([e for e in executions if e.status == "cancelled"])
        
        # Calculate average duration
        durations = []
        for execution in executions:
            if execution.started_at and execution.completed_at:
                duration = (execution.completed_at - execution.started_at).total_seconds()
                durations.append(duration)
        
        average_duration = sum(durations) / len(durations) if durations else 0
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        return {
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": failed,
            "cancelled_executions": cancelled,
            "average_duration": round(average_duration, 2),
            "success_rate": round(success_rate, 2)
        }
