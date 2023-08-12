from app.services.data_processor import StoreDataProcessor
from app.services.file_upload import CSVUploader


class ReportGenerator:
    @staticmethod
    def process():

        ## hardcoding timestamp value as suggested due to static data
        current_timestamp = "2023-01-25T18:13:22.479"
        # current_timestamp = datetime.utcnow().isoformat()

        report_data = [
            store_data for store_data in StoreDataProcessor.process(current_timestamp)
        ]

        download_link = CSVUploader("test").upload(report_data)
        return download_link
