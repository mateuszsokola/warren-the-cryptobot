from enum import Enum


class OrderType(str, Enum):
    stop_loss = "Stop Loss"
    take_profit = "Take Profit"
