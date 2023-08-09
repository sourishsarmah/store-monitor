from typing import Any

from pydantic import BaseModel


class Report(BaseModel):
    report_id: str


class ReportResponse(Report):
    report_status: str
    report_result: Any
