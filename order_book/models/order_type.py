from enum import Enum


class OrderType(str, Enum):
    buy = "Buy"
    sell = "Sell"
    stop_loss = "Stop Loss"
    take_profit = "Take Profit"
