# SYSTEM Design


## Database:

- Since our data has relations between them and has a fixed schema, so a relational database with high load handling ability like PostgreSQL is a good bit for the system.

- There are three database tables:

1. `store_hours` : Stores the business hours of the stores
2. `store_tz`: Stores the store's local timezone
3. `store_status`: Stores the store's operation status during a specific timestamp.



## Data Processing

- The dataset is large and can be expected to grow quite rapidly if the number of stores and the frequency of ping responses increases. 
- So, we need to avoid loading all the store data in the application memory and process data in batches in order to do the processing with a `low memory usage` in the application level. This will make sure, even if the number of stores or the frequency of store status data increases, our system remain unaffected.
- In order to achive this, the report generation is done in batches, where only a specific store data is loaded into the memory at a time (using python generators).

```python
class StoreDataProcessor:
    @classmethod
    def process(cls, session, current_timestamp):

        store_ids = store_repo.get_all_store_ids(session)
        ...
        for store_id in store_ids:
            print(f"Processing Store Data for store_id: {store_id}")
            ...

            # generator is used to return a single store report at a time
            yield store_report 
```


## Data Extrapolation

- We only have specific timestamp data with the store operation status.
- First, consideration that is taken is that we will assume the store to always open and close on time.
- Secondly, here it would be wrong to declare a store to be inactive if we don't have a data point indicating so. In this case, the store is assumed to be open unless we have a data point prior to the current timestamp where the store status has changed to inactive from an active status.
- Concluding both the above point, we consider that 
    - store opens on time on its business hours thus, its status is active at the opening time, 
    - then it will remain active untill there is a inactive data point in store status where the timestamp is less than the last active time. 
    - The time period from opening time to inactive status timestamp is considered as active period.
    - And the inactive period start from the inactive timestamp unless again an active timestamp data point is encountered. And so on untill the store closes
For eg.
```
Store A has following working hours
- 11:30 to 15:59 (1st shift)
- 20:00 to 23:59 (2nd shift)

And, we have the following data points in the store status
- 12:30 -> inactive
- 13:00 -> active
- 15:00 -> inactive

There, we will have the following active/ inactive time period according to our extrapolation algorithm:

- 11:30 to 12:29 -> active (1 hour)
- 12:30 to 12:59 -> inactive (30 mins)
- 13:00 to 15:00 -> active (2 hours)
- 15:00 to 15:59 -> inactive (1 hours)
And since we don't have any data points for the second shift we will consider the timeperiod of the business hours to be active
- 20:00 to 23:59 -> active  (3 hours)
```

