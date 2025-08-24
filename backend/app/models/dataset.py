from sqlalchemy import Column, String, Text, DateTime, JSON, Enum as SQLEnum, Integer, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum

from app.core.database import Base

class SourceType(str, Enum):
    FILE = "file"
    SQL = "sql"
    S3 = "s3"
    API = "api"

# SQLAlchemy models for database
class DatasetModel(Base):
    """SQLAlchemy model for datasets"""
    __tablename__ = "datasets"
    
    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)
    source_path = Column(String, nullable=True)
    source_connection = Column(JSON, nullable=True)
    tags = Column(ARRAY(String), default=list)
    owner_id = Column(String, nullable=False, index=True)
    last_profiled_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class DatasetProfileModel(Base):
    """SQLAlchemy model for dataset profiles"""
    __tablename__ = "dataset_profiles"
    
    id = Column(String, primary_key=True)
    dataset_id = Column(String, nullable=False, index=True)
    schema = Column(JSON, nullable=False)  # Column types, null counts, etc.
    row_count_estimate = Column(Integer, nullable=True)
    preview_data = Column(JSON, nullable=True)  # Top 5 rows
    statistics = Column(JSON, nullable=True)  # Min, max, unique counts, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic models for API requests/responses
from pydantic import BaseModel, Field

class DatasetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    source_type: SourceType
    source_path: Optional[str] = None
    source_connection: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)

class DatasetCreate(DatasetBase):
    pass

class DatasetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    source_type: Optional[SourceType] = None
    source_path: Optional[str] = None
    source_connection: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class DatasetInDB(DatasetBase):
    id: str
    owner_id: str
    last_profiled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Dataset(DatasetBase):
    id: str
    owner_id: str
    last_profiled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DatasetProfile(BaseModel):
    """Dataset profiling information"""
    id: str
    dataset_id: str
    schema: Dict[str, Any]  # Column types, null counts, etc.
    row_count_estimate: Optional[int] = None
    preview_data: Optional[List[Dict[str, Any]]] = None  # Top 5 rows
    statistics: Optional[Dict[str, Any]] = None  # Min, max, unique counts, etc.
    created_at: datetime

    class Config:
        from_attributes = True

class ColumnSchema(BaseModel):
    """Individual column schema"""
    name: str
    dtype: str
    null_count: int
    unique_count: Optional[int] = None
    min_value: Optional[Union[str, int, float]] = None
    max_value: Optional[Union[str, int, float]] = None
    mean_value: Optional[float] = None
    sample_values: List[Any] = Field(default_factory=list)

class DatasetStatistics(BaseModel):
    """Statistical summary of dataset"""
    total_rows: int
    total_columns: int
    memory_usage_mb: Optional[float] = None
    duplicate_rows: Optional[int] = None
    missing_values_percentage: Optional[float] = None
    data_quality_score: Optional[float] = None

class DatasetPreview(BaseModel):
    """Dataset preview for UI display"""
    dataset: Dataset
    profile: Optional[DatasetProfile] = None
    sample_rows: List[Dict[str, Any]] = Field(default_factory=list)
    column_info: List[ColumnSchema] = Field(default_factory=list)

class DatasetUpload(BaseModel):
    """Dataset upload request"""
    name: str
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    auto_profile: bool = True

class DatasetSearch(BaseModel):
    """Dataset search parameters"""
    query: Optional[str] = None
    tags: Optional[List[str]] = None
    source_type: Optional[SourceType] = None
    owner_id: Optional[str] = None
    limit: int = 50
    offset: int = 0

class DatasetLineage(BaseModel):
    """Dataset lineage information"""
    dataset_id: str
    upstream_datasets: List[str] = Field(default_factory=list)
    downstream_datasets: List[str] = Field(default_factory=list)
    blocks_reading: List[str] = Field(default_factory=list)
    blocks_writing: List[str] = Field(default_factory=list)
    last_updated: datetime 