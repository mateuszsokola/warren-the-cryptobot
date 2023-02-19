from enum import Enum


class StrategyStatus(str, Enum):
    active = "Active"
    cancelled = "Cancelled"
