from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class RunBase(BaseModel):
    project_id: str
    kernel_id: Optional[str] = None

class RunCreate(RunBase):
    pass

class RunUpdate(BaseModel):
    status: Optional[RunStatus] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None

class RunInDB(RunBase):
    id: str
    status: RunStatus = RunStatus.PENDING
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Run(RunBase):
    id: str
    status: RunStatus
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class BlockRunBase(BaseModel):
    block_id: str

class BlockRunCreate(BlockRunBase):
    run_id: str

class BlockRunUpdate(BaseModel):
    status: Optional[RunStatus] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None

class BlockRunInDB(BlockRunBase):
    id: str
    run_id: str
    status: RunStatus = RunStatus.PENDING
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class BlockRun(BlockRunBase):
    id: str
    run_id: str
    status: RunStatus
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class RunWithBlocks(Run):
    """Run with its block executions"""
    block_runs: List[BlockRun] = []

class ExecutionRequest(BaseModel):
    """Request to execute blocks"""
    project_id: str
    block_ids: List[str] = Field(..., min_items=1)
    kernel_id: Optional[str] = None
    force: bool = False
    incremental: bool = True

class ExecutionResponse(BaseModel):
    """Response to execution request"""
    run_id: str
    status: RunStatus
    message: str
    estimated_duration: Optional[int] = None  # in seconds 