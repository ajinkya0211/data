from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from app.core.database import Base

class BlockKind(str, Enum):
    CODE = "code"
    MARKDOWN = "markdown"
    SQL = "sql"
    TEXT = "text"

class BlockLanguage(str, Enum):
    PYTHON = "python"
    SQL = "sql"
    MARKDOWN = "markdown"
    TEXT = "text"

class BlockStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STALE = "stale"

class Block(Base):
    """SQLAlchemy model for blocks"""
    __tablename__ = "blocks"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False, index=True)
    owner_id = Column(String, nullable=False, index=True)
    kind = Column(String(50), nullable=False)
    language = Column(String(50), nullable=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    status = Column(String(50), default="idle")
    
    # Output storage fields
    outputs = Column(JSON, default=list)
    last_execution_output = Column(Text, nullable=True)
    last_execution_error = Column(Text, nullable=True)
    execution_count = Column(Integer, default=0)
    
    block_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Pydantic models for API requests/responses
from pydantic import BaseModel, Field

class BlockBase(BaseModel):
    kind: str  # Use string instead of enum for API compatibility
    language: Optional[str] = None  # Use string instead of enum
    title: Optional[str] = None
    content: Optional[str] = None
    position_x: int = 0
    position_y: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BlockCreate(BlockBase):
    project_id: str

class BlockUpdate(BaseModel):
    kind: Optional[str] = None  # Use string instead of enum
    language: Optional[str] = None  # Use string instead of enum
    title: Optional[str] = None
    content: Optional[str] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class BlockInDB(BlockBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BlockResponse(BaseModel):
    """Block response model for API"""
    id: str
    project_id: str
    owner_id: str
    kind: str
    language: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    position_x: int = 0
    position_y: int = 0
    status: str
    outputs: List[Dict[str, Any]] = []
    last_execution_output: Optional[str] = None
    last_execution_error: Optional[str] = None
    execution_count: int = 0
    block_metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BlockWithOutputs(BaseModel):
    """Block with its latest outputs - Pydantic model for API responses"""
    id: str
    project_id: str
    owner_id: str
    kind: str  # Use string instead of enum
    language: Optional[str] = None  # Use string instead of enum
    title: Optional[str] = None
    content: Optional[str] = None
    position_x: int = 0
    position_y: int = 0
    status: str  # Use string instead of enum
    outputs: List[Dict[str, Any]] = []
    last_execution_output: Optional[str] = None
    last_execution_error: Optional[str] = None
    execution_count: int = 0
    block_metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    last_run: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class BlockExecutionRequest(BaseModel):
    """Request to execute a block"""
    block_ids: List[str]
    session_id: Optional[str] = None
    force: bool = False

class BlockExecutionResult(BaseModel):
    """Result of block execution"""
    block_id: str
    session_id: str
    status: str  # Use string instead of enum
    execution_time_ms: Optional[int] = None
    outputs: List[Dict[str, Any]] = []
    error: Optional[str] = None

class BlockMetadata(BaseModel):
    """Extended metadata for blocks"""
    tags: List[str] = Field(default_factory=list)
    kernel_id: Optional[str] = None
    ai_notes: Optional[str] = None
    dataset_refs: List[str] = Field(default_factory=list)
    data_profile_ref: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    estimated_runtime: Optional[int] = None  # in seconds
    memory_usage: Optional[int] = None  # in MB

class BlockTemplate(BaseModel):
    """Template for creating new blocks"""
    name: str
    description: str 