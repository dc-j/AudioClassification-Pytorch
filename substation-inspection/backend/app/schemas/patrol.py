from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PatrolTaskCreate(BaseModel):
    name: str
    station_id: int
    type: str
    plan_date: datetime
    executor: Optional[str] = None
    device_count: int = 0
    point_count: int = 0
    route_config: Optional[str] = None


class PatrolTaskUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    executor: Optional[str] = None
    progress: Optional[float] = None


class PatrolTaskResponse(BaseModel):
    id: int
    name: str
    station_id: int
    type: str
    status: str
    plan_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    executor: Optional[str] = None
    device_count: int
    point_count: int
    progress: float

    class Config:
        from_attributes = True


class PatrolStatistics(BaseModel):
    total: int
    executing: int
    completed: int
    paused: int
    smart: int
