from typing import Any

from pydantic import BaseModel


class Report(BaseModel):
    report_id: str


class ReportResponse(Report):
    report_status: str
    report_result: Any


class ReportOutput:
    store_id: int
    uptime_last_hour: int
    uptime_last_day: int
    update_last_week: int
    downtime_last_hour: int
    downtime_last_day: int
    downtime_last_week: int
