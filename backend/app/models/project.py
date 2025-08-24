from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.core.database import Base

class Project(Base):
    """SQLAlchemy model for projects"""
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String, nullable=False, index=True)
    is_public = Column(Boolean, default=False)
    project_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    workflows = relationship("WorkflowDefinition", back_populates="project")

# Pydantic models for API requests/responses
from pydantic import BaseModel, Field

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class ProjectInDB(ProjectBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectResponse(ProjectBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True
        alias_generator = lambda x: "project_metadata" if x == "metadata" else x

class ProjectPatch(BaseModel):
    """JSON Patch operation for projects"""
    op: str  # add, remove, replace, copy, move, test
    path: str
    value: Optional[Any] = None

class PatchOperation(BaseModel):
    """Single patch operation"""
    op: str
    path: str
    value: Optional[Any] = None

class ProjectWithBlocks(BaseModel):
    """Project with its blocks"""
    project: ProjectResponse
    blocks: List[Any]  # Will be Block objects
    
    class Config:
        from_attributes = True

class ProjectExport(BaseModel):
    """Project export format"""
    project: ProjectResponse
    blocks: List[Any]  # Will be Block objects
    edges: List[Any]   # Will be Edge objects
    metadata: Dict[str, Any]

class ProjectVersion(BaseModel):
    """Project version information"""
    version: str
    created_at: datetime
    changes: List[str]
    author_id: str 