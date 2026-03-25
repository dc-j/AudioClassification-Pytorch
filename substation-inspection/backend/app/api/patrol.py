from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.patrol import PatrolTask, PatrolRecord
from ..schemas.patrol import PatrolTaskCreate, PatrolTaskUpdate, PatrolTaskResponse, PatrolStatistics
from ..schemas.common import ResponseModel
from datetime import datetime, timezone

router = APIRouter(prefix="/patrol", tags=["智能巡检"])


@router.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(PatrolTask).order_by(PatrolTask.created_at.desc()).all()
    return ResponseModel(data=[PatrolTaskResponse.model_validate(t) for t in tasks])


@router.post("/tasks")
def create_task(req: PatrolTaskCreate, db: Session = Depends(get_db)):
    task = PatrolTask(**req.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return ResponseModel(data=PatrolTaskResponse.model_validate(task))


@router.put("/tasks/{task_id}")
def update_task(task_id: int, req: PatrolTaskUpdate, db: Session = Depends(get_db)):
    task = db.query(PatrolTask).filter(PatrolTask.id == task_id).first()
    if not task:
        return ResponseModel(code=404, message="任务不存在")
    update_data = req.model_dump(exclude_unset=True)
    if update_data.get("status") == "executing" and not task.start_time:
        update_data["start_time"] = datetime.now(timezone.utc)
    elif update_data.get("status") == "completed":
        update_data["end_time"] = datetime.now(timezone.utc)
    for key, value in update_data.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return ResponseModel(data=PatrolTaskResponse.model_validate(task))


@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db)):
    total = db.query(PatrolTask).count()
    executing = db.query(PatrolTask).filter(PatrolTask.status == "executing").count()
    completed = db.query(PatrolTask).filter(PatrolTask.status == "completed").count()
    paused = db.query(PatrolTask).filter(PatrolTask.status == "paused").count()
    return ResponseModel(data=PatrolStatistics(
        total=total, executing=executing, completed=completed, paused=paused, smart=0
    ))


@router.get("/records")
def list_records(db: Session = Depends(get_db)):
    records = db.query(PatrolRecord).order_by(PatrolRecord.recorded_at.desc()).limit(100).all()
    return ResponseModel(data=[
        {
            "id": r.id,
            "task_id": r.task_id,
            "result": r.result,
            "detail": r.detail,
            "temperature": r.temperature,
            "recorded_at": r.recorded_at,
        }
        for r in records
    ])
