from enum import Enum


class StoreStatusEnum(Enum):
    active = "active"
    inactive = "inactive"


class ReportStatusEnum(Enum):
    pending = "Pending"
    running = "Running"
    complete = "Complete"
    failed = "Failed"
