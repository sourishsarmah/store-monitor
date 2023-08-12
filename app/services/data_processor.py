import warnings
from datetime import datetime, time, timedelta

import pandas as pd
import pytz

from app.crud.store import StoreRepo
from app.schemas import ReportOutput

warnings.filterwarnings("ignore")


class StoreDataProcessor:
    @classmethod
    def process(cls, session, current_timestamp) -> ReportOutput:
        store_repo = StoreRepo()
        store_ids = store_repo.get_all_store_ids(session)

        curr_timstamp_utc = datetime.fromisoformat(current_timestamp).replace(
            tzinfo=pytz.utc
        )

        for store_id in store_ids:
            print(f"Processing Store Data for store_id: {store_id}")

            store_hours_data = store_repo.get_working_hours(session, store_id)
            store_hours_data = cls.__process_working_hours(store_hours_data, store_id)
            store_status_data = store_repo.get_data_from_id(
                session, store_id, current_timestamp
            )

            store_timezone_str = store_status_data["timezone_str"].iloc[0]

            curr_timestamp_local = curr_timstamp_utc.astimezone(
                pytz.timezone(store_timezone_str)
            )
            processed_data = cls.__process_store_data(
                store_status_data, store_hours_data
            )
            store_report = cls.extract_info(processed_data, curr_timestamp_local)
            yield store_report

    @classmethod
    def extract_info(
        cls, processed_store_data: pd.DataFrame, current_timestamp
    ) -> ReportOutput:

        uptime_last_hour, downtime_last_hour = cls.__extract_last_hour_info(
            processed_store_data, current_timestamp
        )

        report = {
            "store_id": processed_store_data["store_id"].iloc[0],
            "uptime_last_hour": uptime_last_hour,
            "uptime_last_day": cls.__extract_last_day_info(
                processed_store_data[processed_store_data["status"] == "active"],
                current_timestamp,
            ),
            "update_last_week": cls.__extract_last_week_info(
                processed_store_data[processed_store_data["status"] == "active"]
            ),
            "downtime_last_hour": downtime_last_hour,
            "downtime_last_day": cls.__extract_last_day_info(
                processed_store_data[processed_store_data["status"] == "inactive"],
                current_timestamp,
            ),
            "downtime_last_week": cls.__extract_last_week_info(
                processed_store_data[processed_store_data["status"] == "inactive"]
            ),
        }

        return report

    @classmethod
    def __extract_last_week_info(cls, dataframe: pd.DataFrame) -> int:
        last_week_data = dataframe["time_diff"].sum() / 60
        return last_week_data

    @classmethod
    def __extract_last_day_info(
        cls, dataframe: pd.DataFrame, curr_timestamp_local
    ) -> int:
        last_day = (curr_timestamp_local - timedelta(days=1)).date()
        last_day_df = dataframe[dataframe["date_local"] == last_day]
        last_day_data = last_day_df["time_diff"].sum() / 60
        return last_day_data

    @classmethod
    def __extract_last_hour_info(
        cls, dataframe: pd.DataFrame, curr_timestamp_local
    ) -> (int, int):
        last_hour_timestamp = curr_timestamp_local - timedelta(hours=1)
        last_hour_date = last_hour_timestamp.date()
        last_hour = last_hour_timestamp.hour
        last_hour_df = dataframe[(dataframe["date_local"] == last_hour_date)]
        last_hour_df = last_hour_df[
            (
                (last_hour_df["time_local"] >= time(hour=last_hour))
                & (last_hour_df["time_local"] < time(hour=last_hour + 1))
            )
            | (
                (last_hour_df["status_end_time"] >= time(hour=last_hour))
                & (last_hour_df["status_end_time"] < time(hour=last_hour + 1))
            )
        ]

        if len(last_hour_df):
            last_hour_df["time_local"].iloc[0] = time(hour=last_hour)
            last_hour_df["status_end_time"].iloc[-1] = time(hour=last_hour + 1)
            last_hour_df["time_diff"] = last_hour_df[
                ["status_end_time", "time_local"]
            ].apply(lambda x: cls.__cal_time_diff(x), axis=1)
            last_active_hour_data = last_hour_df[last_hour_df["status"] == "active"][
                "time_diff"
            ].sum()
            last_inactive_hour_data = last_hour_df[
                last_hour_df["status"] == "inactive"
            ]["time_diff"].sum()
        else:
            last_active_hour_data = 60
            last_inactive_hour_data = 0

        return last_active_hour_data, last_inactive_hour_data

    @classmethod
    def __process_store_data(
        cls, store_data: pd.DataFrame, store_hours: pd.DataFrame
    ) -> pd.DataFrame:
        store_agg_work_hours = cls.__agg_store_working_hours(store_hours)

        store_id = store_data["store_id"].iloc[0]

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

            status_df["time_diff"] = status_df[["status_end_time", "time_local"]].apply(
                lambda x: cls.__cal_time_diff(x), axis=1
            )

            status_df["date_local"] = idx[0]
            status_df["day"] = idx[1]

            status_df["store_id"] = store_id

            def get_timestamp_local(row):
                return datetime.combine(row[0], row[1])

            status_df["start_timestamp_local"] = status_df[
                ["date_local", "time_local"]
            ].apply(lambda x: get_timestamp_local(x), axis=1)
            status_df["end_timestamp_local"] = status_df[
                ["date_local", "status_end_time"]
            ].apply(lambda x: get_timestamp_local(x), axis=1)
            processed_dfs.append(status_df)

        return pd.concat(processed_dfs)

    @classmethod
    def __process_working_hours(cls, data: pd.DataFrame, store_id) -> pd.DataFrame:
        days_of_week = list(range(0, 7))
        days = data["day"].values.tolist()
        remaining_days = list(set(days_of_week) - set(days))

        default_data = pd.DataFrame(
            {
                "store_id": [store_id] * len(remaining_days),
                "day": remaining_days,
                "start_time_local": [time(0, 0)] * len(remaining_days),
                "end_time_local": [time(23, 59, 59)] * len(remaining_days),
            }
        )
        store_hours_df = pd.concat([data, default_data], ignore_index=True)
        return store_hours_df

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

    @staticmethod
    def __cal_time_diff(row):
        """
        Calculate the active/inactive interval duration in minutes
        """
        dummy_date = datetime(2023, 1, 1)
        diff = datetime.combine(dummy_date, row["status_end_time"]) - datetime.combine(
            dummy_date, row["time_local"]
        )
        return diff.total_seconds() / 60
