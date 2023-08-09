from datetime import datetime, time

from sqlalchemy import VARCHAR, BigInteger, Column, DateTime, Enum, Integer, Time
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.schemas import StatusEnum


class StoreHours(Base):

    __tablename__ = "store_hours"
    store_id = Column(BigInteger, index=True)
    day = Column(Integer)
    start_time_local = Column(
        Time, nullable=False, server_default=str(time(hour=00, minute=00, second=00))
    )
    end_time_local = Column(
        Time, nullable=False, server_default=str(time(hour=23, minute=59, second=59))
    )
    __mapper_args__ = {"primary_key": [store_id, day, start_time_local]}


class StoreTimezone(Base):
    __tablename__ = "store_tz"
    store_id = Column(BigInteger, primary_key=True, index=True)
    timezone_str = Column(VARCHAR(32), server_default="America/Chicago")


class StoreStatus(Base):
    __tablename__ = "store_status"
    store_id = Column(BigInteger, index=True)
    timestamp_utc = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(StatusEnum))
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow()
    )

    __mapper_args__ = {"primary_key": [store_id, timestamp_utc]}
