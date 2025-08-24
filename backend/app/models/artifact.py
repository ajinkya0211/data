from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ArtifactType(str, Enum):
    STREAM = "stream"
    DISPLAY = "display"
    HTML = "html"
    PNG = "png"
    TABLE = "table"
    ERROR = "error"
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"

class ArtifactBase(BaseModel):
    type: ArtifactType
    mime_type: Optional[str] = None
    storage_path: str
    size_bytes: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ArtifactCreate(ArtifactBase):
    block_run_id: str

class ArtifactUpdate(BaseModel):
    type: Optional[ArtifactType] = None
    mime_type: Optional[str] = None
    storage_path: Optional[str] = None
    size_bytes: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class ArtifactInDB(ArtifactBase):
    id: str
    block_run_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class Artifact(ArtifactBase):
    id: str
    block_run_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ArtifactContent(BaseModel):
    """Artifact with its content for display"""
    artifact: Artifact
    content: Optional[Any] = None
    content_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

class TableArtifact(BaseModel):
    """Table-specific artifact metadata"""
    columns: List[str]
    rows: List[List[Any]]
    total_rows: int
    schema: Dict[str, str]  # column_name: dtype

class ImageArtifact(BaseModel):
    """Image-specific artifact metadata"""
    width: int
    height: int
    format: str
    thumbnail_path: Optional[str] = None

class StreamArtifact(BaseModel):
    """Stream output artifact"""
    stream_type: str  # stdout, stderr
    content: str
    timestamp: datetime 