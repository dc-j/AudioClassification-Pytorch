from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.device import Device
from ..schemas.common import ResponseModel

router = APIRouter(prefix="/devices", tags=["设备管理"])


@router.get("")
def list_devices(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return ResponseModel(data=[
        {
            "id": d.id,
            "name": d.name,
            "code": d.code,
            "type": d.type,
            "model": d.model,
            "ip_address": d.ip_address,
            "protocol": d.protocol,
            "status": d.status,
            "area": d.area,
        }
        for d in devices
    ])


@router.get("/status")
def device_status_summary(db: Session = Depends(get_db)):
    types = ["camera", "robot", "infrared", "rail_robot"]
    result = {}
    for t in types:
        total = db.query(Device).filter(Device.type == t).count()
        online = db.query(Device).filter(Device.type == t, Device.status == "online").count()
        result[t] = {"total": total, "online": online}
    return ResponseModel(data=result)
