from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.alarm import Alarm
from ..schemas.alarm import AlarmResponse, AlarmHandleRequest
from ..schemas.common import ResponseModel, PaginatedResponse
from typing import Optional
from datetime import datetime, timezone

router = APIRouter(prefix="/alarms", tags=["智能告警"])


@router.get("")
def list_alarms(
    level: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Alarm)
    if level:
        query = query.filter(Alarm.level == level)
    if status:
        query = query.filter(Alarm.status == status)
    total = query.count()
    alarms = query.order_by(Alarm.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[AlarmResponse.model_validate(a) for a in alarms],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.put("/{alarm_id}")
def handle_alarm(alarm_id: int, req: AlarmHandleRequest, db: Session = Depends(get_db)):
    alarm = db.query(Alarm).filter(Alarm.id == alarm_id).first()
    if not alarm:
        return ResponseModel(code=404, message="告警不存在")
    alarm.status = req.status
    alarm.handler = req.handler
    alarm.handle_note = req.handle_note
    alarm.handle_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alarm)
    return ResponseModel(data=AlarmResponse.model_validate(alarm))
