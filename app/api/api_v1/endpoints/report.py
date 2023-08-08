from typing import Any

from fastapi import APIRouter

from app import schemas

router = APIRouter()


@router.get("/get_report/{report_id}", response_model=schemas.ReportResponse)
def read_users(report_id: str) -> Any:
    """
    Retrieve users.
    """
    return {"report_id": report_id}


@router.post("/trigger_report", response_model=schemas.ReportResponse)
def create_user() -> Any:
    """
    Create new user.
    """

    return {"report_id": "null"}
