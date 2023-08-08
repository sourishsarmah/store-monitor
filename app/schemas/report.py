from pydantic import BaseModel


class Report(BaseModel):
    report_id: str


class ReportResponse(BaseModel):
    report_id: str
