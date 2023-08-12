from typing import Any

from fastapi import APIRouter, Depends

from app import schemas
from app.api.deps import get_db
from app.crud.report import ReportRepo
from app.worker import generate_report

router = APIRouter()


@router.get("/get_report/{report_id}", response_model=schemas.ReportResponse)
def read_users(report_id: str, db=Depends(get_db)) -> Any:
    """
    Retrieve users.
    """
    report = ReportRepo.get(db, report_id)
    print(report.__dict__)
    return report.__dict__


@router.post("/trigger_report", response_model=schemas.Report)
def trigger_report(db=Depends(get_db)) -> Any:
    """
    Create new user.
    """
    task = generate_report.delay()
    ReportRepo().create(db, task.id)
    return {"report_id": task.id}
