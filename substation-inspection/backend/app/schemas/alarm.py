from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AlarmResponse(BaseModel):
    id: int
    level: str
    source: str
    type: str
    content: str
    area: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlarmHandleRequest(BaseModel):
    status: str
    handler: str
    handle_note: Optional[str] = None
