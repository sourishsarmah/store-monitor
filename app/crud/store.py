import pandas as pd


class StoreRepo:
    @classmethod
    def get_data_from_id(cls, session, store_id, timestamp) -> pd.DataFrame:
        results_df = pd.read_sql_query(
            """
                select 
                b.store_id, 
                b.timestamp_utc, 
                b.timestamp_local::date as date_local,
                b.timestamp_local::time as time_local,
                status, 
                b."day", 
                b.timezone_str 
                from 
                (
                    select 
                    a.store_id, 
                    status, 
                    timestamp_utc at TIME zone 'UTC' as timestamp_utc,
                    coalesce(store_tz.timezone_str, 'America/Chicago') as timezone_str, 
                    timestamp_utc AT TIME ZONE coalesce(store_tz.timezone_str, 'America/Chicago') as timestamp_local,
                    extract(dow from (timestamp_utc AT TIME ZONE coalesce(store_tz.timezone_str, 'America/Chicago'))) as "day"
                    from 
                    (
                        SELECT store_status.store_id, timestamp_utc, status
                        from store_status 
                        where store_status.store_id = %(store_id)s 
                        and timestamp_utc between %(current_timestamp)s::date - interval '1 week' and %(current_timestamp)s
                    ) a
                    left join store_tz 
                    on a.store_id = store_tz.store_id
                ) as b """,
            con=session.get_bind(),
            params={"store_id": store_id, "current_timestamp": timestamp},
        )

        return results_df

    @classmethod
    def get_all_store_ids(cls, session) -> list:
        results = session.execute("SELECT distinct store_id FROM store_status")

        results = [result[0] for result in results]

        return results

    @classmethod
    def get_working_hours(cls, session, store_id) -> pd.DataFrame:
        results_df = pd.read_sql_query(
            """
                select * from store_hours 
                where store_id = %(store_id)s """,
            con=session.get_bind(),
            params={"store_id": store_id},
        )

        return results_df
