from pydantic import BaseModel
from typing import Optional, Union, Dict, Any, List
from enum import Enum


class Status(Enum):
    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILED = "failure"


class FileResponse(BaseModel):
    id: int
    filepath: str
    file_metadata: Optional[Dict[str, Any]]
    text: List
    status: str

