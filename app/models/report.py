import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.schemas import ReportStatusEnum


class Report(Base):
    __tablename__ = "report"

    report_id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4())
    status = Column(Enum(ReportStatusEnum), nullable=False)
    download_link = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow()
    )
    update_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )
