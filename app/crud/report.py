from app.models import Report
from app.schemas import ReportStatusEnum


class ReportRepo:
    @classmethod
    def update_status(cls, session, report_id: str, status: ReportStatusEnum):
        session.query(Report).filter(Report.report_id == report_id).update(
            {"status": status}
        )
        session.commit()
        return True

    @classmethod
    def update_download_link(cls, session, report_id: str, link: str):
        session.query(Report).filter(Report.report_id == report_id).update(
            {"download_link": link}
        )
        session.commit()
        return True

    @classmethod
    def create(cls, session, report_id):
        report = Report(report_id=report_id, status=ReportStatusEnum.pending)
        session.add(report)
        session.commit()
        return True

    @classmethod
    def get(cls, session, report_id):
        report = session.query(Report).filter(Report.report_id == report_id).first()
        return report
