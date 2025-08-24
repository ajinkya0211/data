"""
MCP (Model Context Protocol) Context Service
Provides rich, context-aware information for AI decision making
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import structlog
from dataclasses import dataclass
from enum import Enum

logger = structlog.get_logger()

class ContextType(str, Enum):
    PROJECT = "project"
    DATASET = "dataset"
    WORKFLOW = "workflow"
    USER = "user"
    SYSTEM = "system"
    EXECUTION = "execution"

@dataclass
class MCPContext:
    """Rich context information for AI decision making"""
    context_id: str
    context_type: ContextType
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None
    priority: int = 1

class MCPContextService:
    """
    Service for managing rich context information for AI agents
    Provides context-aware insights for intelligent decision making
    """
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.context_cache: Dict[str, MCPContext] = {}
        self.context_relationships: Dict[str, List[str]] = {}
        
    async def get_project_context(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive project context for AI decision making
        
        Returns rich context including:
        - Project structure and metadata
        - Block relationships and dependencies
        - Execution history and patterns
        - Data profiles and insights
        - User behavior patterns
        - Performance metrics
        """
        try:
            from app.services.block_service import BlockService
            from app.services.project_service import ProjectService
            from app.services.dataset_service import DatasetService
            from app.services.workflow_orchestrator import WorkflowOrchestrator
            
            # Initialize services
            block_service = BlockService(self.db_session)
            project_service = ProjectService(self.db_session)
            dataset_service = DatasetService(self.db_session)
            orchestrator = WorkflowOrchestrator(self.db_session)
            
            # Get project information
            project = await project_service.get_project(project_id, user_id)
            blocks = await block_service.get_project_blocks(project_id, user_id)
            
            # Get execution history
            execution_history = await self._get_execution_history(project_id, user_id)
            
            # Get data insights
            data_insights = await self._get_data_insights(project_id, user_id)
            
            # Get user patterns
            user_patterns = await self._get_user_patterns(user_id, project_id)
            
            # Get performance metrics
            performance_metrics = await self._get_performance_metrics(project_id, user_id)
            
            # Build comprehensive context
            context = {
                "project": {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "created_at": project.created_at.isoformat() if project.created_at else None,
                    "updated_at": project.updated_at.isoformat() if project.updated_at else None,
                    "metadata": project.project_metadata or {}
                },
                "blocks": {
                    "total": len(blocks),
                    "by_type": self._categorize_blocks(blocks),
                    "by_status": self._categorize_by_status(blocks),
                    "relationships": await self._analyze_block_relationships(blocks),
                    "execution_history": execution_history,
                    "recent_errors": await self._get_recent_errors(blocks, user_id)
                },
                "data": {
                    "datasets": data_insights.get("datasets", []),
                    "profiles": data_insights.get("profiles", []),
                    "quality_metrics": data_insights.get("quality_metrics", []),
                    "transformation_history": data_insights.get("transformation_history", [])
                },
                "user": {
                    "patterns": user_patterns,
                    "preferences": await self._get_user_preferences(user_id),
                    "expertise_level": await self._assess_user_expertise(user_id, project_id)
                },
                "performance": {
                    "metrics": performance_metrics,
                    "bottlenecks": await self._identify_bottlenecks(project_id, user_id),
                    "optimization_opportunities": await self._find_optimization_opportunities(project_id, user_id)
                },
                "workflow": {
                    "execution_patterns": await self._analyze_execution_patterns(project_id, user_id),
                    "dependency_graph": await self._build_dependency_graph(blocks),
                    "parallelization_opportunities": await self._find_parallelization_opportunities(blocks)
                },
                "system": {
                    "available_tools": await self._get_available_tools(),
                    "resource_usage": await self._get_resource_usage(),
                    "best_practices": await self._get_best_practices(project_id, user_id)
                }
            }
            
            # Cache the context
            context_id = f"project_{project_id}_{user_id}"
            mcp_context = MCPContext(
                context_id=context_id,
                context_type=ContextType.PROJECT,
                data=context,
                metadata={
                    "project_id": project_id,
                    "user_id": user_id,
                    "generated_at": datetime.utcnow().isoformat(),
                    "context_version": "1.0"
                },
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(minutes=30),
                priority=1
            )
            
            self.context_cache[context_id] = mcp_context
            
            logger.info("Generated rich project context", 
                       project_id=project_id,
                       user_id=user_id,
                       context_size=len(str(context)))
            
            return context
            
        except Exception as e:
            logger.error("Failed to generate project context", 
                        project_id=project_id,
                        error=str(e))
            raise
    
    async def get_dataset_context(self, dataset_id: str, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dataset context for AI decision making"""
        try:
            from app.services.dataset_service import DatasetService
            
            dataset_service = DatasetService(self.db_session)
            dataset = await dataset_service.get_dataset(dataset_id, user_id)
            profile = await dataset_service.get_latest_profile(dataset_id)
            
            # Analyze dataset characteristics
            schema_analysis = await self._analyze_dataset_schema(profile)
            quality_insights = await self._analyze_data_quality(profile)
            transformation_suggestions = await self._suggest_transformations(profile)
            
            context = {
                "dataset": {
                    "id": dataset.id,
                    "name": dataset.name,
                    "description": dataset.description,
                    "source_type": dataset.source_type,
                    "size_bytes": dataset.size_bytes,
                    "created_at": dataset.created_at.isoformat() if dataset.created_at else None
                },
                "profile": {
                    "schema": schema_analysis,
                    "statistics": profile.statistics if profile else {},
                    "quality_metrics": quality_insights,
                    "anomalies": await self._detect_data_anomalies(profile),
                    "patterns": await self._identify_data_patterns(profile)
                },
                "transformations": {
                    "suggestions": transformation_suggestions,
                    "common_patterns": await self._get_common_transformation_patterns(profile),
                    "optimization_tips": await self._get_transformation_optimization_tips(profile)
                },
                "usage": {
                    "workflows_used_in": await self._get_workflow_usage(dataset_id),
                    "transformation_history": await self._get_transformation_history(dataset_id),
                    "performance_metrics": await self._get_dataset_performance_metrics(dataset_id)
                }
            }
            
            return context
            
        except Exception as e:
            logger.error("Failed to generate dataset context", 
                        dataset_id=dataset_id,
                        error=str(e))
            raise
    
    async def get_workflow_context(self, workflow_id: str, user_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow execution context"""
        try:
            from app.services.workflow_orchestrator import WorkflowOrchestrator
            
            orchestrator = WorkflowOrchestrator(self.db_session)
            execution = await orchestrator.get_workflow_status(workflow_id)
            logs = await orchestrator.get_workflow_logs(workflow_id)
            
            # Analyze execution patterns
            execution_analysis = await self._analyze_execution_patterns(workflow_id, user_id)
            performance_insights = await self._analyze_workflow_performance(execution, logs)
            optimization_suggestions = await self._suggest_workflow_optimizations(execution, logs)
            
            context = {
                "workflow": {
                    "id": workflow_id,
                    "status": execution.status.value if execution else "unknown",
                    "execution_time": execution.completed_at - execution.started_at if execution and execution.completed_at else None,
                    "total_nodes": len(execution.nodes) if execution else 0,
                    "completed_nodes": len([n for n in execution.node_status.values() if n.value == "completed"]) if execution else 0
                },
                "execution": {
                    "patterns": execution_analysis,
                    "performance": performance_insights,
                    "bottlenecks": await self._identify_execution_bottlenecks(execution, logs),
                    "optimizations": optimization_suggestions
                },
                "logs": {
                    "total_events": len(logs),
                    "key_events": self._extract_key_events(logs),
                    "error_patterns": await self._analyze_error_patterns(logs)
                }
            }
            
            return context
            
        except Exception as e:
            logger.error("Failed to generate workflow context", 
                        workflow_id=workflow_id,
                        error=str(e))
            raise
    
    # === PRIVATE HELPER METHODS ===
    
    async def _get_execution_history(self, project_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get execution history for the project"""
        # This would query execution logs and history
        return []
    
    async def _get_data_insights(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Get data insights and profiles"""
        # This would analyze datasets and their profiles
        return {
            "datasets": [],
            "profiles": [],
            "quality_metrics": [],
            "transformation_history": []
        }
    
    async def _get_user_patterns(self, user_id: str, project_id: str) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        # This would analyze user's historical behavior
        return {
            "common_operations": [],
            "preferred_block_types": [],
            "execution_frequency": "medium",
            "error_tolerance": "low"
        }
    
    async def _get_performance_metrics(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Get performance metrics for the project"""
        # This would analyze execution performance
        return {
            "avg_execution_time": 0.0,
            "success_rate": 1.0,
            "resource_usage": "low",
            "optimization_score": 0.8
        }
    
    def _categorize_blocks(self, blocks: List) -> Dict[str, int]:
        """Categorize blocks by type"""
        categories = {}
        for block in blocks:
            block_type = getattr(block, 'kind', 'unknown')
            categories[block_type] = categories.get(block_type, 0) + 1
        return categories
    
    def _categorize_by_status(self, blocks: List) -> Dict[str, int]:
        """Categorize blocks by status"""
        statuses = {}
        for block in blocks:
            status = getattr(block, 'status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1
        return statuses
    
    async def _analyze_block_relationships(self, blocks: List) -> Dict[str, Any]:
        """Analyze relationships between blocks"""
        # This would analyze data flow and dependencies
        return {
            "data_flow": [],
            "dependencies": [],
            "parallel_groups": []
        }
    
    async def _get_recent_errors(self, blocks: List, user_id: str) -> List[Dict[str, Any]]:
        """Get recent execution errors"""
        # This would query recent error logs
        return []
    
    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences and settings"""
        # This would query user preferences
        return {
            "preferred_language": "python",
            "code_style": "pandas",
            "matplotlib": "matplotlib"
        }
    
    async def _assess_user_expertise(self, user_id: str, project_id: str) -> str:
        """Assess user's expertise level"""
        # This would analyze user's historical performance
        return "intermediate"
    
    async def _identify_bottlenecks(self, project_id: str, user_id: str) -> List[str]:
        """Identify performance bottlenecks"""
        # This would analyze execution patterns
        return []
    
    async def _find_optimization_opportunities(self, project_id: str, user_id: str) -> List[str]:
        """Find optimization opportunities"""
        # This would analyze code and execution patterns
        return []
    
    async def _analyze_execution_patterns(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Analyze execution patterns"""
        # This would analyze historical execution data
        return {}
    
    async def _build_dependency_graph(self, blocks: List) -> Dict[str, Any]:
        """Build dependency graph for blocks"""
        # This would analyze block dependencies
        return {}
    
    async def _find_parallelization_opportunities(self, blocks: List) -> List[str]:
        """Find parallelization opportunities"""
        # This would analyze block independence
        return []
    
    async def _get_available_tools(self) -> List[str]:
        """Get available tools and libraries"""
        return [
            "pandas", "numpy", "matplotlib", "seaborn", "scikit-learn",
            "plotly", "bokeh", "altair", "statsmodels", "scipy"
        ]
    
    async def _get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""
        return {
            "cpu_usage": "low",
            "memory_usage": "low",
            "disk_usage": "low"
        }
    
    async def _get_best_practices(self, project_id: str, user_id: str) -> List[str]:
        """Get best practices for the project"""
        return [
            "Use vectorized operations for better performance",
            "Handle missing values appropriately",
            "Validate data before processing",
            "Use appropriate data types"
        ]
    
    async def _analyze_dataset_schema(self, profile) -> Dict[str, Any]:
        """Analyze dataset schema"""
        if not profile or not profile.schema:
            return {}
        
        return {
            "columns": profile.schema.get("columns", []),
            "data_types": profile.schema.get("data_types", {}),
            "constraints": profile.schema.get("constraints", [])
        }
    
    async def _analyze_data_quality(self, profile) -> Dict[str, Any]:
        """Analyze data quality metrics"""
        if not profile or not profile.statistics:
            return {}
        
        return {
            "missing_values": profile.statistics.get("missing_values_percentage", 0),
            "duplicates": profile.statistics.get("duplicate_rows", 0),
            "outliers": profile.statistics.get("outliers", 0)
        }
    
    async def _suggest_transformations(self, profile) -> List[str]:
        """Suggest data transformations"""
        suggestions = []
        
        if profile and profile.statistics:
            if profile.statistics.get("missing_values_percentage", 0) > 10:
                suggestions.append("Handle missing values (imputation or removal)")
            
            if profile.statistics.get("duplicate_rows", 0) > 0:
                suggestions.append("Remove duplicate rows")
            
            if profile.statistics.get("outliers", 0) > 0:
                suggestions.append("Handle outliers appropriately")
        
        return suggestions
    
    async def _detect_data_anomalies(self, profile) -> List[str]:
        """Detect data anomalies"""
        anomalies = []
        
        if profile and profile.statistics:
            # Add anomaly detection logic
            pass
        
        return anomalies
    
    async def _identify_data_patterns(self, profile) -> List[str]:
        """Identify data patterns"""
        patterns = []
        
        if profile and profile.statistics:
            # Add pattern identification logic
            pass
        
        return patterns
    
    async def _get_common_transformation_patterns(self, profile) -> List[str]:
        """Get common transformation patterns"""
        return [
            "Standardize numerical columns",
            "Encode categorical variables",
            "Feature scaling",
            "Data validation"
        ]
    
    async def _get_transformation_optimization_tips(self, profile) -> List[str]:
        """Get transformation optimization tips"""
        return [
            "Use vectorized operations",
            "Avoid loops when possible",
            "Use appropriate data types",
            "Batch process large datasets"
        ]
    
    async def _get_workflow_usage(self, dataset_id: str) -> List[str]:
        """Get workflows that use this dataset"""
        return []
    
    async def _get_transformation_history(self, dataset_id: str) -> List[Dict[str, Any]]:
        """Get transformation history for dataset"""
        return []
    
    async def _get_dataset_performance_metrics(self, dataset_id: str) -> Dict[str, Any]:
        """Get performance metrics for dataset operations"""
        return {}
    
    async def _analyze_execution_patterns(self, workflow_id: str, user_id: str) -> Dict[str, Any]:
        """Analyze workflow execution patterns"""
        return {}
    
    async def _analyze_workflow_performance(self, execution, logs) -> Dict[str, Any]:
        """Analyze workflow performance"""
        return {}
    
    async def _suggest_workflow_optimizations(self, execution, logs) -> List[str]:
        """Suggest workflow optimizations"""
        return []
    
    async def _identify_execution_bottlenecks(self, execution, logs) -> List[str]:
        """Identify execution bottlenecks"""
        return []
    
    async def _analyze_error_patterns(self, logs) -> Dict[str, Any]:
        """Analyze error patterns in logs"""
        return {}
    
    def _extract_key_events(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract key events from logs"""
        key_events = []
        for log in logs:
            if log.get("event_type") in ["workflow_started", "node_completed", "workflow_completed"]:
                key_events.append(log)
        return key_events
    
    def get_cached_context(self, context_id: str) -> Optional[MCPContext]:
        """Get cached context if still valid"""
        if context_id in self.context_cache:
            context = self.context_cache[context_id]
            if context.expires_at and context.expires_at > datetime.utcnow():
                return context
            else:
                del self.context_cache[context_id]
        return None
    
    def clear_expired_contexts(self):
        """Clear expired contexts from cache"""
        current_time = datetime.utcnow()
        expired_keys = [
            key for key, context in self.context_cache.items()
            if context.expires_at and context.expires_at <= current_time
        ]
        for key in expired_keys:
            del self.context_cache[key]
