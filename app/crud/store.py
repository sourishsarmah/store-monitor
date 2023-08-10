import pandas as pd

from app.db.session import SessionLocal


class StoreRepo:
    @classmethod
    def get_data_from_id(cls, session, store_id, timestamp):
        results_df = pd.read_sql_query(
            """
            select * from 
            (
                select 
                b.store_id, 
                b.timestamp_utc, 
                b.timestamp_local::date as date_local,
                b.timestamp_local::time as time_local,
                status, 
                b."day", 
                coalesce(store_hours.start_time_local, '00:00:00') as start_time_local, 
                coalesce(store_hours.end_time_local, '23:59:00') as end_time_local from 
                (
                    select 
                    a.store_id, 
                    status, 
                    timestamp_utc at TIME zone 'UTC' as timestamp_utc,
                    timestamp_utc AT TIME ZONE coalesce(store_tz.timezone_str, 'America/Chicago') as timestamp_local,
                    extract(dow from (timestamp_utc AT TIME ZONE coalesce(store_tz.timezone_str, 'America/Chicago'))) as "day"
                    from 
                    (
                        SELECT store_status.store_id, timestamp_utc, status
                        from store_status 
                        where store_status.store_id = %(store_id)s 
                        and timestamp_utc between %(current_timestamp)s::timestamp - interval '1 week' and %(current_timestamp)s
                    ) a
                    left join store_tz 
                    on a.store_id = store_tz.store_id
                ) as b
                left join store_hours 
                on b.store_id = store_hours.store_id
                and b."day" = store_hours."day"
            ) as c
            where time_local between start_time_local and end_time_local """,
            con=session.get_bind(),
            params={"store_id": store_id, "current_timestamp": timestamp},
        )

        return results_df
    

    @classmethod
    def get_all_store_ids(cls, session):
        results = session.execute(
            "SELECT distinct store_id FROM store_status"
        )

        results = [result[0] for result in results]

        return results
