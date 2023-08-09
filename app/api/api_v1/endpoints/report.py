from typing import Any

from fastapi import APIRouter

from app import schemas
from app.core.celery_app import celery_app
from app.worker import generate_report

router = APIRouter()


@router.get("/get_report/{report_id}", response_model=schemas.ReportResponse)
def read_users(report_id: str) -> Any:
    """
    Retrieve users.
    """
    task_result = celery_app.AsyncResult(report_id)
    result = {
        "report_id": report_id,
        "report_status": task_result.status,
        "report_result": task_result.result,
    }
    return result


@router.post("/trigger_report", response_model=schemas.Report)
def create_user() -> Any:
    """
    Create new user.
    """
    task = generate_report.delay()
    return {"report_id": task.id}
