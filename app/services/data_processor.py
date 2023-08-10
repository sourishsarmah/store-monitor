import pandas as pd

from app.crud.store import StoreRepo
from app.db.session import SessionLocal
from app.schemas import ReportOutput


class StoreDataProcessor:
    @classmethod
    def process(cls, current_timestamp):
        with SessionLocal() as session:
            store_repo = StoreRepo()
            store_ids = store_repo.get_all_store_ids(session)

            for store_id in store_ids:
                print(f"Procession Store Data for store_id: {store_id}")
                store_data = store_repo.get_data_from_id(
                    session, store_id, current_timestamp
                )
                processed_data = cls.__process_store_data(store_data)
                yield processed_data

    @classmethod
    def __process_store_data(cls, store_data: pd.DataFrame) -> ReportOutput:
        pass
