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

                store_hours_data = store_repo.get_working_hours(session, store_id)
                store_status_data = store_repo.get_data_from_id(
                    session, store_id, current_timestamp
                )

                store_status_data["timezone_str"].iloc[0]
                processed_data = cls.__process_store_data(
                    store_status_data, store_hours_data
                )
                store_report = cls.extract_info(processed_data)
                yield store_report

    @classmethod
    def extract_info(cls, processed_store_data: pd.DataFrame) -> ReportOutput:
        pass

    @classmethod
    def __process_store_data(
        cls, store_data: pd.DataFrame, store_hours: pd.DataFrame
    ) -> pd.DataFrame:
        store_agg_work_hours = cls.__agg_store_working_hours(store_hours)

        store_df = store_data.merge(
            store_hours,
            left_on=["store_id", "day"],
            right_on=["store_id", "day"],
            how="left",
        )

        def in_business_hours(row):
            if (
                row["time_local"] >= row["start_time_local"]
                and row["time_local"] <= row["end_time_local"]
            ):
                return True
            return False

        store_df = store_df[store_df.apply(lambda row: in_business_hours(row), axis=1)]

        ## Grouped data for each day
        store_date_grouped_df = store_df.groupby(["date_local", "day"])
        processed_dfs = []
        for idx, day_df in store_date_grouped_df:

            ## find working business hours of the day
            working_times_list = []
            for working_times in store_agg_work_hours[
                store_agg_work_hours["day"] == day_df["day"].iloc[0]
            ]["working_shifts"].iloc[0]:
                working_times_list.extend([working_times[0], working_times[1]])

            ## add edge times(opening and closing time to the dataset)
            edge_times_df = pd.DataFrame(
                {
                    "time_local": working_times_list,
                    "status": [
                        "active" if i % 2 == 0 else "closing"
                        for i in range(len(working_times_list))
                    ],
                }
            )
            day_df = pd.concat(
                [day_df[["time_local", "status"]], edge_times_df], ignore_index=True
            )

            ## sort according to timestamp
            day_df = day_df.sort_values("time_local").reset_index(drop=True)

            ## Our point of interest is only when there is a status change
            status_df = day_df[day_df["status"].shift() != day_df["status"]]

            ## Using the next time in the sequence as the end period of the particular status
            status_df["status_end_time"] = status_df["time_local"].shift(-1)
            status_df = status_df[status_df["status"] != "closing"]
            status_df["date_local"] = idx[0]
            status_df["day"] = idx[1]
            processed_dfs.append(status_df)

        return pd.concat(processed_dfs)

    @classmethod
    def __agg_store_working_hours(
        cls, store_working_hours: pd.DataFrame
    ) -> pd.DataFrame:
        """
        combines multiple working shifts of the store into an aggregated dataframe
        """
        store_agg_hours_df = (
            store_working_hours.groupby(["store_id", "day"]).agg(list).reset_index()
        )
        store_agg_hours_df["working_shifts"] = store_agg_hours_df.apply(
            lambda row: list(zip(row["start_time_local"], row["end_time_local"])),
            axis=1,
        )
        store_agg_hours_df = store_agg_hours_df[["store_id", "day", "working_shifts"]]

        return store_agg_hours_df
