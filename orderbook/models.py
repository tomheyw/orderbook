from enum import Enum
from dataclasses import dataclass

class Side(Enum):
    BID = 0
    ASK = 1

@dataclass
class Order:
    order_id: int
    symbol: str
    side: Side
    price: float
    quantity: int

@dataclass
class CancelMessage:
    order_id: int
    symbol: str

@dataclass
class ExecutionMessage:
    order_id: int
    symbol: str
    quantity: int

@dataclass
class PriceLevel:
    price: float
    quantity: int