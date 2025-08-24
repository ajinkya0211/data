from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EdgeBase(BaseModel):
    from_block_id: str
    to_block_id: str

class EdgeCreate(EdgeBase):
    project_id: str

class EdgeUpdate(BaseModel):
    from_block_id: Optional[str] = None
    to_block_id: Optional[str] = None

class EdgeInDB(EdgeBase):
    id: str
    project_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class Edge(EdgeBase):
    id: str
    project_id: str
    created_at: datetime

    class Config:
        from_attributes = True 