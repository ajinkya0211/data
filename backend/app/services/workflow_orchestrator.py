"""
Workflow Orchestrator Service
Integrates DAG execution, block management, and real-time monitoring
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import structlog
import uuid

from app.services.dag_service import DAGService, WorkflowExecution, ExecutionStatus
from app.services.block_service import BlockService
from app.services.python_executor_service import PythonExecutorService
from app.services.workflow_management_service import WorkflowManagementService
from app.services.websocket_service import websocket_service
from app.models.block import BlockStatus, BlockExecutionResult

logger = structlog.get_logger()

class WorkflowOrchestrator:
    """
    Orchestrates workflow execution by integrating DAG, blocks, and real-time monitoring
    """
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.dag_service = DAGService()
        self.block_service = BlockService(db_session)
        self.python_executor = PythonExecutorService(websocket_service)
        self.websocket_service = websocket_service
        self.workflow_management = WorkflowManagementService(db_session)
        self.active_workflows: Dict[str, str] = {}  # workflow_id -> execution_id
    
    async def execute_project_workflow(
        self, 
        project_id: str, 
        user_id: str,
        block_ids: Optional[List[str]] = None,
        workflow_definition_id: Optional[str] = None
    ) -> WorkflowExecution:
        """
        Execute all blocks in a project as a workflow
        
        Args:
            project_id: Project to execute
            user_id: User executing the workflow
            block_ids: Optional specific blocks to execute (if None, executes all)
            workflow_definition_id: Optional specific workflow definition to use
            
        Returns:
            WorkflowExecution instance with real-time updates
        """
        try:
            logger.info("Starting project workflow execution", 
                       project_id=project_id, user_id=user_id)
            
            # Get or create workflow definition
            if workflow_definition_id:
                workflow_def = await self.workflow_management.get_workflow_definition(workflow_definition_id)
                if not workflow_def:
                    raise ValueError(f"Workflow definition {workflow_definition_id} not found")
            else:
                # Auto-generate workflow definition
                workflow_result = await self.workflow_management.create_or_update_project_workflow(
                    project_id, user_id
                )
                
                if not workflow_result['success']:
                    raise ValueError(f"Failed to create workflow: {workflow_result['error']}")
                
                workflow_def = workflow_result['workflow_definition']
            
            # Get blocks for execution
            if block_ids:
                # Use specific blocks
                blocks = []
                for block_id in block_ids:
                    block = await self.block_service.get_block(block_id, user_id)
                    if block:
                        blocks.append(block)
                
                # Filter to only include blocks in the workflow definition
                workflow_block_ids = set(workflow_def.nodes)
                blocks = [b for b in blocks if b.id in workflow_block_ids]
            else:
                # Use all blocks from workflow definition
                blocks = []
                for block_id in workflow_def.nodes:
                    block = await self.block_service.get_block(block_id, user_id)
                    if block:
                        blocks.append(block)
            
            if not blocks:
                raise ValueError("No blocks found for execution")
            
            # Filter executable blocks (CODE blocks)
            executable_blocks = [block for block in blocks if block.kind.lower() == 'code']
            
            if not executable_blocks:
                raise ValueError("No executable code blocks found")
            
            logger.info("Workflow execution setup completed",
                       project_id=project_id,
                       total_blocks=len(blocks),
                       executable_blocks=len(executable_blocks),
                       workflow_definition_id=workflow_def.id)
            
            # Create workflow execution record
            execution = await self.workflow_management.create_workflow_execution(
                workflow_definition_id=workflow_def.id,
                project_id=project_id,
                user_id=user_id
            )
            
            # Start execution session
            session_id = await self.python_executor.start_execution_session(f"workflow_{execution.id}")
            
            # Update execution with session ID
            await self.workflow_management.update_execution_status(
                execution.id, "running", session_id=session_id
            )
            
            # Execute the workflow using DAG service
            dag_execution = await self.dag_service.execute_workflow(
                workflow_id=str(execution.id),
                nodes=[block.id for block in executable_blocks],
                edges=workflow_def.edges,
                node_executor=lambda block_id, session_id, content=None: 
                    self._execute_block_node(block_id, session_id, user_id, execution.id),
                block_service=self.block_service,
                session_id=session_id
            )
            
            # Update execution with results
            await self.workflow_management.update_execution_status(
                execution.id,
                "completed" if dag_execution.status == ExecutionStatus.COMPLETED else "failed",
                node_results=dag_execution.node_results,
                node_status={node: status.value for node, status in dag_execution.node_status.items()}
            )
            
            logger.info("Workflow execution completed", 
                       execution_id=execution.id,
                       status=dag_execution.status.value)
            
            return execution
            
        except Exception as e:
            logger.error("Workflow execution failed", 
                        project_id=project_id, user_id=user_id, error=str(e))
            
            # Update execution status if we have one
            if 'execution' in locals():
                await self.workflow_management.update_execution_status(
                    execution.id, "failed", error_message=str(e)
                )
            
            raise
    
    async def _execute_block_node(self, block_id: str, session_id: str, 
                                user_id: str, execution_id: str) -> BlockExecutionResult:
        """
        Execute a single block node in the workflow
        
        Args:
            block_id: Block to execute
            session_id: Python execution session ID
            user_id: User executing the workflow
            execution_id: Workflow execution ID
            
        Returns:
            BlockExecutionResult
        """
        try:
            logger.info("Executing block node", block_id=block_id, execution_id=execution_id)
            
            # Get block
            block = await self.block_service.get_block(block_id, user_id)
            if not block:
                raise ValueError(f"Block {block_id} not found")
            
            # Update workflow execution to show current node
            await self.workflow_management.update_execution_status(
                execution_id, "running", current_node=block_id
            )
            
            # Execute the block
            execution_result = await self.python_executor.execute_code(
                session_id, block.content, block_id
            )
            
            # Store execution result in block metadata
            await self.block_service.update_block_execution_result(
                block_id, execution_result, user_id
            )
            
            # Update workflow execution with node result
            current_results = {}
            current_status = {}
            
            # Get current execution to update
            execution = await self.workflow_management.get_workflow_execution(execution_id)
            if execution and execution.node_results:
                current_results = execution.node_results
                current_status = execution.node_status or {}
            
            current_results[block_id] = execution_result
            current_status[block_id] = "completed" if not execution_result.error else "failed"
            
            await self.workflow_management.update_execution_status(
                execution_id,
                "running",
                node_results=current_results,
                node_status=current_status
            )
            
            logger.info("Block node execution completed", 
                       block_id=block_id, execution_id=execution_id,
                       success=not execution_result.error)
            
            return execution_result
            
        except Exception as e:
            logger.error("Block node execution failed", 
                        block_id=block_id, execution_id=execution_id, error=str(e))
            
            # Create error result
            error_result = BlockExecutionResult(
                block_id=block_id,
                session_id=session_id,
                status="failed",
                error=str(e),
                outputs=[]
            )
            
            # Update workflow execution with error
            current_results = {}
            current_status = {}
            
            execution = await self.workflow_management.get_workflow_execution(execution_id)
            if execution and execution.node_results:
                current_results = execution.node_results
                current_status = execution.node_status or {}
            
            current_results[block_id] = error_result
            current_status[block_id] = "failed"
            
            await self.workflow_management.update_execution_status(
                execution_id,
                "running",
                node_results=current_results,
                node_status=current_status
            )
            
            return error_result
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowExecution]:
        """Get the current status of a workflow execution"""
        return await self.workflow_management.get_workflow_execution(workflow_id)
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        return await self.workflow_management.cancel_workflow_execution(workflow_id)
    
    async def get_project_workflow_info(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow information for a project"""
        try:
            # Get workflow definition
            workflow_def = await self.workflow_management.get_project_workflow(project_id)
            
            if not workflow_def:
                return {
                    "has_workflow": False,
                    "workflow_definition": None,
                    "recent_executions": [],
                    "statistics": {}
                }
            
            # Get recent executions
            recent_executions = await self.workflow_management.list_project_executions(project_id, limit=10)
            
            # Get execution statistics
            statistics = await self.workflow_management.get_execution_statistics(project_id)
            
            return {
                "has_workflow": True,
                "workflow_definition": {
                    "id": str(workflow_def.id),
                    "name": workflow_def.name,
                    "description": workflow_def.description,
                    "nodes": workflow_def.nodes,
                    "edges": workflow_def.edges,
                    "execution_order": workflow_def.execution_order,
                    "version": workflow_def.version,
                    "created_at": workflow_def.created_at.isoformat(),
                    "updated_at": workflow_def.updated_at.isoformat()
                },
                "recent_executions": [
                    {
                        "id": str(exec.id),
                        "status": exec.status,
                        "started_at": exec.started_at.isoformat() if exec.started_at else None,
                        "completed_at": exec.completed_at.isoformat() if exec.completed_at else None,
                        "current_node": exec.current_node
                    }
                    for exec in recent_executions
                ],
                "statistics": statistics
            }
            
        except Exception as e:
            logger.error("Failed to get project workflow info", 
                        project_id=project_id, error=str(e))
            return {
                "has_workflow": False,
                "error": str(e)
            }
    
    def _create_websocket_callback(self, project_id: str, user_id: str):
        """Create a WebSocket callback for workflow events"""
        async def callback(event_type: str, data: Dict[str, Any]):
            try:
                # Broadcast to project subscribers
                await self.websocket_service.broadcast_execution_event(
                    f"project_{project_id}",
                    event_type,
                    {
                        "project_id": project_id,
                        "user_id": user_id,
                        **data
                    }
                )
            except Exception as e:
                logger.warning("Workflow callback failed", error=str(e))
        
        return callback
    
    async def get_workflow_logs(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get logs for a workflow execution"""
        execution_id = self.active_workflows.get(workflow_id)
        if execution_id:
            return self.dag_service.get_execution_logs(execution_id)
        return []
    
    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get information about all active workflows"""
        active = []
        for workflow_id, execution_id in self.active_workflows.items():
            execution = self.dag_service.get_execution_status(execution_id)
            if execution:
                active.append({
                    "workflow_id": workflow_id,
                    "execution_id": execution_id,
                    "status": execution.status.value,
                    "started_at": execution.started_at.isoformat() if execution.started_at else None,
                    "nodes_count": len(execution.nodes),
                    "completed_nodes": len([n for n in execution.node_status.values() if n == ExecutionStatus.COMPLETED]),
                    "failed_nodes": len([n for n in execution.node_status.values() if n == ExecutionStatus.FAILED])
                })
        return active
    
    # === DEPENDENCY ANALYSIS ===
    
    async def analyze_block_dependencies(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """
        Analyze dependencies between blocks in a project
        (Future enhancement: parse variable usage to detect real dependencies)
        """
        try:
            blocks = await self.block_service.get_project_blocks(project_id, user_id)
            
            # For now, simple analysis based on block order
            # Future: parse code to detect variable dependencies
            
            analysis = {
                "total_blocks": len(blocks),
                "executable_blocks": len([b for b in blocks if b.kind.lower() == 'code']),
                "dependencies": [],
                "execution_order": [block.id for block in blocks if block.kind.lower() == 'code'],
                "estimated_execution_time": len(blocks) * 2  # rough estimate in seconds
            }
            
            return analysis
            
        except Exception as e:
            logger.error("Dependency analysis failed", error=str(e))
            return {"error": str(e)}
    
    # === PERFORMANCE MONITORING ===
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics and performance metrics"""
        try:
            dag_executions = self.dag_service.execution_history
            python_executions = self.python_executor.execution_history
            
            return {
                "workflow_executions": {
                    "total": len(dag_executions),
                    "completed": len([e for e in dag_executions if e.status == ExecutionStatus.COMPLETED]),
                    "failed": len([e for e in dag_executions if e.status == ExecutionStatus.FAILED]),
                    "active": len(self.active_workflows)
                },
                "block_executions": {
                    "total": len(python_executions),
                    "successful": len([e for e in python_executions if e.get("status") == "completed"]),
                    "failed": len([e for e in python_executions if e.get("status") == "failed"])
                },
                "performance": {
                    "avg_workflow_duration": self._calculate_avg_workflow_duration(),
                    "avg_block_execution_time": self._calculate_avg_block_time()
                }
            }
            
        except Exception as e:
            logger.error("Failed to get execution statistics", error=str(e))
            return {"error": str(e)}
    
    def _calculate_avg_workflow_duration(self) -> float:
        """Calculate average workflow duration in seconds"""
        completed_workflows = [
            e for e in self.dag_service.execution_history 
            if e.status == ExecutionStatus.COMPLETED and e.started_at and e.completed_at
        ]
        
        if not completed_workflows:
            return 0.0
        
        total_duration = sum([
            (e.completed_at - e.started_at).total_seconds() 
            for e in completed_workflows
        ])
        
        return total_duration / len(completed_workflows)
    
    def _calculate_avg_block_time(self) -> float:
        """Calculate average block execution time in milliseconds"""
        block_executions = [
            e for e in self.python_executor.execution_history 
            if e.get("execution_time_ms") is not None
        ]
        
        if not block_executions:
            return 0.0
        
        total_time = sum([e["execution_time_ms"] for e in block_executions])
        return total_time / len(block_executions)
