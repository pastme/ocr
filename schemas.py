from pydantic import BaseModel
from typing import Optional, Union, Dict, Any


class FileResponse(BaseModel):
    id: int
    filepath: str
    metadata: Optional[Dict[str, Any]]
    text: Optional[Union[str, Dict[str, Any]]]
