from app.crud.report import ReportRepo, ReportStatusEnum
from app.db.session import SessionLocal
from app.services.data_processor import StoreDataProcessor
from app.services.file_upload import CSVUploader


class ReportGenerator:
    @staticmethod
    def process(report_id):

        ## hardcoding timestamp value as suggested due to static data
        current_timestamp = "2023-01-25T18:13:22.479"
        # current_timestamp = datetime.utcnow().isoformat()

        download_link = None

        with SessionLocal() as session:
            report_repo = ReportRepo()
            report_repo.update_status(session, report_id, ReportStatusEnum.running)
            try:
                report_data = [
                    store_data
                    for store_data in StoreDataProcessor.process(
                        session, current_timestamp
                    )
                ]

                download_link = CSVUploader(report_id).upload(report_data)

                report_repo.update_status(session, report_id, ReportStatusEnum.complete)
                report_repo.update_download_link(session, report_id, download_link)

            except Exception as e:
                print("Error: Error while generating report. ", str(e))
                report_repo.update_status(session, report_id, ReportStatusEnum.failed)

        return download_link
