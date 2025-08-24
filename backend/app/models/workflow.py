"""
Workflow Definition Models
Stores DAG definitions and workflow metadata
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class WorkflowDefinition(Base):
    """Workflow definition with DAG structure"""
    
    __tablename__ = "workflow_definitions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # DAG structure
    nodes = Column(JSON, nullable=False)  # List of block IDs
    edges = Column(JSON, nullable=False)  # List of [from_id, to_id] pairs
    execution_order = Column(JSON, nullable=False)  # Topologically sorted execution order
    
    # Metadata
    dependency_map = Column(JSON, nullable=True)  # Detailed dependency information
    is_active = Column(Boolean, default=True)
    version = Column(String(50), default="1.0.0")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="workflows")
    executions = relationship("WorkflowExecution", back_populates="workflow_definition")

class WorkflowExecution(Base):
    """Instance of workflow execution"""
    
    __tablename__ = "workflow_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_definition_id = Column(String, ForeignKey("workflow_definitions.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Execution status
    status = Column(String(50), default="pending")  # pending, running, completed, failed, cancelled
    current_node = Column(String(255), nullable=True)  # Currently executing node
    
    # Execution metadata
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    total_duration = Column(String(50), nullable=True)  # Human readable duration
    
    # Results
    node_results = Column(JSON, nullable=True)  # Results from each node
    node_status = Column(JSON, nullable=True)  # Status of each node
    error_message = Column(Text, nullable=True)
    
    # Session management
    session_id = Column(String(255), nullable=True)  # Python execution session
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workflow_definition = relationship("WorkflowDefinition", back_populates="executions")
    project = relationship("Project")
    user = relationship("User")

# Pydantic models for API requests/responses
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class WorkflowDefinitionCreate(BaseModel):
    """Request to create a workflow definition"""
    project_id: str
    name: str
    description: Optional[str] = None
    nodes: List[str]
    edges: List[List[str]]  # [from_id, to_id] pairs
    execution_order: List[str]
    dependency_map: Optional[Dict[str, Any]] = None

class WorkflowDefinitionUpdate(BaseModel):
    """Request to update a workflow definition"""
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[str]] = None
    edges: Optional[List[List[str]]] = None
    execution_order: Optional[List[str]] = None
    dependency_map: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    version: Optional[str] = None

class WorkflowDefinitionResponse(BaseModel):
    """Response with workflow definition"""
    id: str
    project_id: str
    name: str
    description: Optional[str] = None
    nodes: List[str]
    edges: List[List[str]]
    execution_order: List[str]
    dependency_map: Optional[Dict[str, Any]] = None
    is_active: bool
    version: str
    created_at: datetime
    updated_at: datetime

class WorkflowExecutionRequest(BaseModel):
    """Request to execute a workflow"""
    project_id: str
    workflow_definition_id: Optional[str] = None  # If None, auto-generate from project
    force: bool = False
    parallel: bool = False

class WorkflowExecutionResponse(BaseModel):
    """Response with workflow execution details"""
    execution_id: str
    workflow_definition_id: str
    project_id: str
    status: str
    current_node: Optional[str] = None
    started_at: Optional[datetime] = None
    total_duration: Optional[str] = None
    node_results: Optional[Dict[str, Any]] = None
    node_status: Optional[Dict[str, str]] = None
    error_message: Optional[str] = None

class WorkflowStatusResponse(BaseModel):
    """Response with workflow execution status"""
    execution_id: str
    workflow_definition_id: str
    project_id: str
    status: str
    current_node: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration: Optional[str] = None
    total_nodes: int
    completed_nodes: int
    failed_nodes: int
    error_message: Optional[str] = None
