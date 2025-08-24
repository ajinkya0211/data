from typing import List, Dict, Any, Optional, Set, Tuple, Callable
import structlog
from collections import defaultdict, deque
import asyncio
from datetime import datetime
from enum import Enum
import uuid

logger = structlog.get_logger()

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class WorkflowExecution:
    """Represents a workflow execution instance"""
    def __init__(self, workflow_id: str, nodes: List[str], edges: List[Tuple[str, str]]):
        self.id = str(uuid.uuid4())
        self.workflow_id = workflow_id
        self.nodes = nodes
        self.edges = edges
        self.status = ExecutionStatus.PENDING
        self.node_status: Dict[str, ExecutionStatus] = {node: ExecutionStatus.PENDING for node in nodes}
        self.node_results: Dict[str, Any] = {}
        self.node_start_times: Dict[str, datetime] = {}
        self.node_end_times: Dict[str, datetime] = {}
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.logs: List[Dict[str, Any]] = []

class DAGService:
    """Service for managing Directed Acyclic Graph operations and execution"""
    
    def __init__(self):
        self.logger = logger
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.execution_history: List[WorkflowExecution] = []
        self._execution_callbacks: Dict[str, List[Callable]] = defaultdict(list)
    
    def validate_dag(self, nodes: List[str], edges: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Validate that the graph is a DAG (no cycles)
        
        Args:
            nodes: List of node IDs
            edges: List of (from_node, to_node) tuples
            
        Returns:
            Dict with validation results
        """
        try:
            # Build adjacency list
            graph = defaultdict(list)
            in_degree = defaultdict(int)
            
            for node in nodes:
                in_degree[node] = 0
            
            for from_node, to_node in edges:
                graph[from_node].append(to_node)
                in_degree[to_node] += 1
            
            # Check for cycles using DFS
            visited = set()
            rec_stack = set()
            
            def has_cycle_dfs(node: str) -> bool:
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        if has_cycle_dfs(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
                
                rec_stack.remove(node)
                return False
            
            # Check each node for cycles
            for node in nodes:
                if node not in visited:
                    if has_cycle_dfs(node):
                        return {
                            "is_valid": False,
                            "error": "Cycle detected in graph",
                            "cycle_nodes": list(rec_stack)
                        }
            
            # If no cycles, check if it's a valid DAG
            return {
                "is_valid": True,
                "error": None,
                "cycle_nodes": [],
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
            
        except Exception as e:
            logger.error("DAG validation failed", error=str(e))
            return {
                "is_valid": False,
                "error": f"Validation error: {str(e)}",
                "cycle_nodes": []
            }
    
    def topological_sort(self, nodes: List[str], edges: List[Tuple[str, str]]) -> List[str]:
        """
        Perform topological sort on the DAG
        
        Args:
            nodes: List of node IDs
            edges: List of (from_node, to_node) tuples
            
        Returns:
            Topologically sorted list of nodes
        """
        try:
            # Build adjacency list and in-degree count
            graph = defaultdict(list)
            in_degree = defaultdict(int)
            
            for node in nodes:
                in_degree[node] = 0
            
            for from_node, to_node in edges:
                graph[from_node].append(to_node)
                in_degree[to_node] += 1
            
            # Kahn's algorithm for topological sort
            queue = deque([node for node in nodes if in_degree[node] == 0])
            result = []
            
            while queue:
                node = queue.popleft()
                result.append(node)
                
                for neighbor in graph[node]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
            
            # Check if all nodes were processed
            if len(result) != len(nodes):
                logger.warning("Topological sort incomplete - possible cycle")
                return []
            
            return result
            
        except Exception as e:
            logger.error("Topological sort failed", error=str(e))
            return []
    
    def get_execution_order(self, nodes: List[str], edges: List[Tuple[str, str]]) -> List[str]:
        """
        Get the execution order for nodes in a DAG
        
        Args:
            nodes: List of node IDs
            edges: List of (from_node, to_node) tuples
            
        Returns:
            List of nodes in execution order
        """
        return self.topological_sort(nodes, edges)
    
    def get_dependent_nodes(self, target_node: str, nodes: List[str], edges: List[Tuple[str, str]]) -> Set[str]:
        """
        Get all nodes that depend on the target node (downstream)
        
        Args:
            target_node: The node to find dependents for
            nodes: List of all node IDs
            edges: List of (from_node, to_node) tuples
            
        Returns:
            Set of dependent node IDs
        """
        try:
            # Build reverse adjacency list
            reverse_graph = defaultdict(list)
            for from_node, to_node in edges:
                reverse_graph[to_node].append(from_node)
            
            # DFS to find all dependents
            dependents = set()
            visited = set()
            
            def find_dependents(node: str):
                visited.add(node)
                dependents.add(node)
                
                for dependent in reverse_graph[node]:
                    if dependent not in visited:
                        find_dependents(dependent)
            
            find_dependents(target_node)
            return dependents
            
        except Exception as e:
            logger.error("Failed to get dependent nodes", error=str(e))
            return set()
    
    def get_dependency_nodes(self, target_node: str, nodes: List[str], edges: List[Tuple[str, str]]) -> Set[str]:
        """
        Get all nodes that the target node depends on (upstream)
        
        Args:
            target_node: The node to find dependencies for
            nodes: List of all node IDs
            edges: List of (from_node, to_node) tuples
            
        Returns:
            Set of dependency node IDs
        """
        try:
            # Build adjacency list
            graph = defaultdict(list)
            for from_node, to_node in edges:
                graph[from_node].append(to_node)
            
            # DFS to find all dependencies
            dependencies = set()
            visited = set()
            
            def find_dependencies(node: str):
                visited.add(node)
                dependencies.add(node)
                
                for dependency in graph[node]:
                    if dependency not in visited:
                        find_dependencies(dependency)
            
            find_dependencies(target_node)
            return dependencies
            
        except Exception as e:
            logger.error("Failed to get dependency nodes", error=str(e))
            return set()
    
    def get_affected_nodes(self, changed_nodes: List[str], nodes: List[str], edges: List[Tuple[str, str]]) -> Set[str]:
        """
        Get all nodes that are affected by changes to the specified nodes
        
        Args:
            changed_nodes: List of nodes that have changed
            nodes: List of all node IDs
            edges: List of (from_node, to_node) tuples
            
        Returns:
            Set of affected node IDs
        """
        try:
            affected = set()
            
            for changed_node in changed_nodes:
                # Get all downstream dependents
                dependents = self.get_dependent_nodes(changed_node, nodes, edges)
                affected.update(dependents)
            
            return affected
            
        except Exception as e:
            logger.error("Failed to get affected nodes", error=str(e))
            return set()
    
    def get_parallel_execution_groups(self, nodes: List[str], edges: List[Tuple[str, str]]) -> List[List[str]]:
        """
        Group nodes that can be executed in parallel
        
        Args:
            nodes: List of node IDs
            edges: List of (from_node, to_node) tuples
            
        Returns:
            List of groups, where each group can be executed in parallel
        """
        try:
            # Build adjacency list and in-degree count
            graph = defaultdict(list)
            in_degree = defaultdict(int)
            
            for node in nodes:
                in_degree[node] = 0
            
            for from_node, to_node in edges:
                graph[from_node].append(to_node)
                in_degree[to_node] += 1
            
            # Group nodes by level (nodes with same in-degree can run in parallel)
            groups = []
            current_level = [node for node in nodes if in_degree[node] == 0]
            
            while current_level:
                groups.append(current_level.copy())
                next_level = []
                
                for node in current_level:
                    for neighbor in graph[node]:
                        in_degree[neighbor] -= 1
                        if in_degree[neighbor] == 0:
                            next_level.append(neighbor)
                
                current_level = next_level
            
            return groups
            
        except Exception as e:
            logger.error("Failed to get parallel execution groups", error=str(e))
            return []
    
    def validate_edge_addition(self, from_node: str, to_node: str, nodes: List[str], edges: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Validate if adding an edge would create a cycle
        
        Args:
            from_node: Source node ID
            to_node: Target node ID
            nodes: List of all node IDs
            edges: List of existing edges
            
        Returns:
            Dict with validation results
        """
        try:
            # Check if nodes exist
            if from_node not in nodes or to_node not in nodes:
                return {
                    "is_valid": False,
                    "error": "One or both nodes do not exist"
                }
            
            # Check for self-loops
            if from_node == to_node:
                return {
                    "is_valid": False,
                    "error": "Self-loops are not allowed"
                }
            
            # Check if edge already exists
            if (from_node, to_node) in edges:
                return {
                    "is_valid": False,
                    "error": "Edge already exists"
                }
            
            # Create temporary edges list with new edge
            temp_edges = edges + [(from_node, to_node)]
            
            # Validate DAG
            validation = self.validate_dag(nodes, temp_edges)
            
            if validation["is_valid"]:
                return {
                    "is_valid": True,
                    "error": None
                }
            else:
                return {
                    "is_valid": False,
                    "error": f"Edge would create cycle: {validation['error']}"
                }
                
        except Exception as e:
            logger.error("Edge validation failed", error=str(e))
            return {
                "is_valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    def get_graph_statistics(self, nodes: List[str], edges: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Get statistics about the DAG
        
        Args:
            nodes: List of node IDs
            edges: List of (from_node, to_node) tuples
            
        Returns:
            Dict with graph statistics
        """
        try:
            # Build adjacency list
            graph = defaultdict(list)
            in_degree = defaultdict(int)
            out_degree = defaultdict(int)
            
            for node in nodes:
                in_degree[node] = 0
                out_degree[node] = 0
            
            for from_node, to_node in edges:
                graph[from_node].append(to_node)
                in_degree[to_node] += 1
                out_degree[from_node] += 1
            
            # Find root nodes (no incoming edges)
            root_nodes = [node for node in nodes if in_degree[node] == 0]
            
            # Find leaf nodes (no outgoing edges)
            leaf_nodes = [node for node in nodes if out_degree[node] == 0]
            
            # Calculate depth (longest path from root)
            depth = 0
            if root_nodes:
                depth = self._calculate_max_depth(root_nodes, graph)
            
            return {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "root_nodes": root_nodes,
                "leaf_nodes": leaf_nodes,
                "max_depth": depth,
                "avg_in_degree": sum(in_degree.values()) / len(nodes) if nodes else 0,
                "avg_out_degree": sum(out_degree.values()) / len(nodes) if nodes else 0
            }
            
        except Exception as e:
            logger.error("Failed to get graph statistics", error=str(e))
            return {}
    
    def _calculate_max_depth(self, nodes: List[str], graph: Dict[str, List[str]]) -> int:
        """Helper method to calculate maximum depth from given nodes"""
        if not nodes:
            return 0
        
        max_depth = 0
        visited = set()
        
        def dfs(node: str, current_depth: int):
            nonlocal max_depth
            visited.add(node)
            max_depth = max(max_depth, current_depth)
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor, current_depth + 1)
        
        for node in nodes:
            if node not in visited:
                dfs(node, 1)
        
        return max_depth 
    
    # === EXECUTION ENGINE METHODS ===
    
    async def execute_workflow(
        self, 
        workflow_id: str, 
        nodes: List[str], 
        edges: List[Tuple[str, str]], 
        node_executor: Callable[[str], Any],
        block_service=None,
        session_id: str = None
    ) -> WorkflowExecution:
        """
        Execute a DAG workflow with real-time monitoring
        
        Args:
            workflow_id: Unique identifier for the workflow
            nodes: List of node IDs (block IDs)
            edges: List of (from_node, to_node) tuples
            node_executor: Function to execute individual nodes
            block_service: Block service for fetching block details
            session_id: Execution session ID
            
        Returns:
            WorkflowExecution instance
        """
        try:
            # Validate DAG first
            validation = self.validate_dag(nodes, edges)
            if not validation["is_valid"]:
                raise ValueError(f"Invalid DAG: {validation['error']}")
            
            # Create execution instance
            execution = WorkflowExecution(workflow_id, nodes, edges)
            execution.started_at = datetime.utcnow()
            execution.status = ExecutionStatus.RUNNING
            
            self.active_executions[execution.id] = execution
            
            # Log workflow start
            await self._log_execution_event(execution.id, "workflow_started", {
                "workflow_id": workflow_id,
                "nodes": nodes,
                "edges": edges,
                "session_id": session_id
            })
            
            # Get execution order with parallel groups
            parallel_groups = self.get_parallel_execution_groups(nodes, edges)
            
            logger.info("Starting workflow execution", 
                       execution_id=execution.id, 
                       workflow_id=workflow_id,
                       parallel_groups=len(parallel_groups))
            
            # Execute each parallel group
            for group_index, group in enumerate(parallel_groups):
                if execution.status == ExecutionStatus.FAILED:
                    break
                    
                await self._log_execution_event(execution.id, "group_started", {
                    "group_index": group_index,
                    "nodes": group
                })
                
                # Execute nodes in parallel within the group
                group_tasks = []
                for node_id in group:
                    task = self._execute_node(
                        execution, 
                        node_id, 
                        node_executor, 
                        block_service,
                        session_id
                    )
                    group_tasks.append(task)
                
                # Wait for all nodes in the group to complete
                group_results = await asyncio.gather(*group_tasks, return_exceptions=True)
                
                # Check for failures in the group
                for i, result in enumerate(group_results):
                    node_id = group[i]
                    if isinstance(result, Exception):
                        execution.node_status[node_id] = ExecutionStatus.FAILED
                        execution.status = ExecutionStatus.FAILED
                        execution.error_message = str(result)
                        
                        await self._log_execution_event(execution.id, "node_failed", {
                            "node_id": node_id,
                            "error": str(result)
                        })
                        
                        logger.error("Node execution failed", 
                                   execution_id=execution.id,
                                   node_id=node_id, 
                                   error=str(result))
                        break
                
                await self._log_execution_event(execution.id, "group_completed", {
                    "group_index": group_index,
                    "nodes": group
                })
            
            # Complete execution
            execution.completed_at = datetime.utcnow()
            if execution.status != ExecutionStatus.FAILED:
                execution.status = ExecutionStatus.COMPLETED
            
            await self._log_execution_event(execution.id, "workflow_completed", {
                "status": execution.status.value,
                "duration_seconds": (execution.completed_at - execution.started_at).total_seconds()
            })
            
            # Move to history
            self.execution_history.append(execution)
            if execution.id in self.active_executions:
                del self.active_executions[execution.id]
            
            logger.info("Workflow execution completed", 
                       execution_id=execution.id,
                       status=execution.status.value)
            
            return execution
            
        except Exception as e:
            logger.error("Workflow execution failed", error=str(e))
            if 'execution' in locals():
                execution.status = ExecutionStatus.FAILED
                execution.error_message = str(e)
                execution.completed_at = datetime.utcnow()
            raise
    
    async def _execute_node(
        self, 
        execution: WorkflowExecution, 
        node_id: str, 
        node_executor: Callable[[str], Any],
        block_service=None,
        session_id: str = None
    ) -> Any:
        """Execute a single node in the workflow"""
        try:
            execution.node_status[node_id] = ExecutionStatus.RUNNING
            execution.node_start_times[node_id] = datetime.utcnow()
            
            await self._log_execution_event(execution.id, "node_started", {
                "node_id": node_id
            })
            
            # Get block details if block service is provided
            block_content = None
            if block_service:
                # This would need to be implemented with proper async call
                # block = await block_service.get_block(node_id)
                # block_content = block.content if block else None
                pass
            
            # Execute the node
            result = await node_executor(node_id, session_id, block_content)
            
            execution.node_results[node_id] = result
            execution.node_status[node_id] = ExecutionStatus.COMPLETED
            execution.node_end_times[node_id] = datetime.utcnow()
            
            duration = (execution.node_end_times[node_id] - execution.node_start_times[node_id]).total_seconds()
            
            await self._log_execution_event(execution.id, "node_completed", {
                "node_id": node_id,
                "duration_seconds": duration,
                "result_summary": str(result)[:200] if result else None
            })
            
            # Notify callbacks
            await self._notify_callbacks(execution.id, "node_completed", {
                "node_id": node_id,
                "result": result
            })
            
            logger.info("Node executed successfully", 
                       execution_id=execution.id,
                       node_id=node_id,
                       duration=duration)
            
            return result
            
        except Exception as e:
            execution.node_status[node_id] = ExecutionStatus.FAILED
            execution.node_end_times[node_id] = datetime.utcnow()
            
            await self._log_execution_event(execution.id, "node_failed", {
                "node_id": node_id,
                "error": str(e)
            })
            
            raise e
    
    async def _log_execution_event(self, execution_id: str, event_type: str, data: Dict[str, Any]):
        """Log an execution event with timestamp"""
        if execution_id in self.active_executions:
            log_entry = {
                "timestamp": datetime.utcnow(),
                "event_type": event_type,
                "data": data
            }
            self.active_executions[execution_id].logs.append(log_entry)
    
    async def _notify_callbacks(self, execution_id: str, event_type: str, data: Dict[str, Any]):
        """Notify registered callbacks about execution events"""
        callbacks = self._execution_callbacks.get(execution_id, [])
        for callback in callbacks:
            try:
                await callback(event_type, data)
            except Exception as e:
                logger.warning("Execution callback failed", error=str(e))
    
    def register_execution_callback(self, execution_id: str, callback: Callable):
        """Register a callback for execution events"""
        self._execution_callbacks[execution_id].append(callback)
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get the current status of a workflow execution"""
        if execution_id in self.active_executions:
            return self.active_executions[execution_id]
        
        # Check history
        for execution in self.execution_history:
            if execution.id == execution_id:
                return execution
        
        return None
    
    def get_active_executions(self) -> List[WorkflowExecution]:
        """Get all currently active workflow executions"""
        return list(self.active_executions.values())
    
    def get_execution_logs(self, execution_id: str) -> List[Dict[str, Any]]:
        """Get execution logs for a workflow"""
        execution = self.get_execution_status(execution_id)
        return execution.logs if execution else []
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running workflow execution"""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution.status = ExecutionStatus.FAILED
            execution.error_message = "Execution cancelled by user"
            execution.completed_at = datetime.utcnow()
            
            await self._log_execution_event(execution_id, "workflow_cancelled", {
                "cancelled_at": execution.completed_at
            })
            
            # Move to history
            self.execution_history.append(execution)
            del self.active_executions[execution_id]
            
            logger.info("Workflow execution cancelled", execution_id=execution_id)
            return True
        
        return False