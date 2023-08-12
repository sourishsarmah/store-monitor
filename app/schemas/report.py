from pydantic import BaseModel

from .enum import ReportStatusEnum


class Report(BaseModel):
    report_id: str


class ReportResponse(Report):
    status: ReportStatusEnum
    download_link: str


class ReportOutput:
    store_id: int
    uptime_last_hour: int
    uptime_last_day: int
    uptime_last_week: int
    downtime_last_hour: int
    downtime_last_day: int
    downtime_last_week: int
