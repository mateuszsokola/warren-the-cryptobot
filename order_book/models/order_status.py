from enum import Enum


class OrderStatus(str, Enum):
    active = "Active"
    executed = "Executed"
    cancelled = "Cancelled"
