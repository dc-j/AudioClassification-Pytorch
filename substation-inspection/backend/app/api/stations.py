from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.station import Station
from ..schemas.common import ResponseModel
from typing import List

router = APIRouter(prefix="/stations", tags=["变电站"])


@router.get("")
def list_stations(db: Session = Depends(get_db)):
    stations = db.query(Station).all()
    return ResponseModel(data=[
        {
            "id": s.id,
            "name": s.name,
            "code": s.code,
            "voltage_level": s.voltage_level,
            "status": s.status,
        }
        for s in stations
    ])


@router.get("/{station_id}")
def get_station(station_id: int, db: Session = Depends(get_db)):
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        return ResponseModel(code=404, message="变电站不存在")
    return ResponseModel(data={
        "id": station.id,
        "name": station.name,
        "code": station.code,
        "voltage_level": station.voltage_level,
        "address": station.address,
        "status": station.status,
        "description": station.description,
    })
