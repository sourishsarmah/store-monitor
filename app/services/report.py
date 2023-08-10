from app.services.data_processor import StoreDataProcessor


class ReportGenerator:
    @staticmethod
    def process():

        ## hardcoding timestamp value as suggested due to static data
        current_timestamp = "2023-01-25T18:13:22.479"
        # current_timestamp = datetime.utcnow().isoformat()

        for store_data in StoreDataProcessor.process(current_timestamp):
            print(store_data)
