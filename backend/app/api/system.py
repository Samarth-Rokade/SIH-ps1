from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services import system_service
from app.utils.response import success

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/status")
def status(db: Session = Depends(get_db)):
    return success(system_service.get_status(db))


@router.get("/data-info")
def data_info(db: Session = Depends(get_db)):
    return success(system_service.get_data_info(db))


@router.get("/models")
def models():
    return success(system_service.get_models())
