from typing import Optional

from pydantic import AnyHttpUrl, BaseModel

from .enum import ReportStatusEnum


class Report(BaseModel):
    report_id: str


class ReportResponse(Report):
    status: ReportStatusEnum
    download_link: Optional[AnyHttpUrl]


class ReportOutput:
    store_id: int
    uptime_last_hour: int
    uptime_last_day: int
    uptime_last_week: int
    downtime_last_hour: int
    downtime_last_day: int
    downtime_last_week: int
