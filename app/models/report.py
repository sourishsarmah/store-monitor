from sqlalchemy import Column, Integer

from app.db.base_class import Base


class Report(Base):
    report_id = Column(Integer, primary_key=True, index=True)
