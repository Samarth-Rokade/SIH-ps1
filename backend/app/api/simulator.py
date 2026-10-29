from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.schemas import SimulatorRequest
from app.services import simulator_service
from app.utils.response import success

router = APIRouter(prefix="/simulator", tags=["simulator"])


@router.get("/{project_id}/parameters")
def parameters(project_id: str, db: Session = Depends(get_db)):
    return success(simulator_service.get_parameters(db, project_id).model_dump(mode="json"))


@router.post("/run")
def run(body: SimulatorRequest, db: Session = Depends(get_db)):
    return success(simulator_service.run(db, body).model_dump(mode="json"))
