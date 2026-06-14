"""
Orderbook time complexities
    on_order: O(log k)
    on_cancel: O(log k)
    on_execute: O(log k)
    get_price_levels: O(k)
    get_quantity: O(d)

Where
    k: no. of price levels
    d: depth of book (price levels traversed from top of book)
"""

from sortedcontainers import SortedDict
from queue import Queue

from .models import CancelMessage, ExecutionMessage, Side, Order, PriceLevel

type Book = SortedDict[float, int]


def notify(func):
    def wrapper(self: Orderbook, *args, **kwargs):
        """Notify subscribers with a snapshot of the orderbook."""
        result = func(self, *args, **kwargs)
        if self.subscriber_queues:
            snapshot = (
                Orderbook.get_price_levels(self.bid_book),
                Orderbook.get_price_levels(self.ask_book),
            )
            for q in self.subscriber_queues:
                q.put(snapshot)
        return result
    return wrapper


class Orderbook:
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.subscriber_queues: list[Queue] = []
        self.orders = {}
        self.bid_book: Book = SortedDict(lambda x: -x)  # desc
        self.ask_book: Book = SortedDict()  # asc

    def subscribe(self) -> Queue:
        """Each subscriber gets its own event queue."""
        q = Queue()
        self.subscriber_queues.append(q)
        return q

    @notify
    def on_order(self, msg: Order) -> None:
        self.orders[msg.order_id] = msg  # O(1)
        book = self.bid_book if msg.side == Side.BID else self.ask_book
        qty = book.get(msg.price, 0)  # O(1)
        book[msg.price] = qty + msg.quantity  # insert: O(log k)

    @notify
    def on_cancel(self, msg: CancelMessage) -> None:
        order = self.orders[msg.order_id]  # O(1)
        book = self.bid_book if order.side == Side.BID else self.ask_book
        book[order.price] -= order.quantity  # O(1)
        if book[order.price] == 0:  # clean empty price-level
            del book[order.price]  # O(log k)

        # update orders dict
        del self.orders[msg.order_id]  # O(1)

    @notify
    def on_execute(self, msg: ExecutionMessage) -> None:
        order = self.orders[msg.order_id]
        book = self.bid_book if order.side == Side.BID else self.ask_book
        book[order.price] -= msg.quantity  # O(1)
        if book[order.price] == 0:
            del book[order.price]  # O(log k)

        # update order
        if order.quantity == msg.quantity:  # fill
            del self.orders[msg.order_id]  # O(1)
        else:
            order.quantity -= msg.quantity

    @staticmethod
    def get_price_levels(book: Book) -> list[PriceLevel]:
        """Snapshot of all price levels for bid/ask side."""
        return [PriceLevel(price=price, quantity=quantity) for price, quantity in book.items()]  # O(k)
    
    @staticmethod
    def get_quantity(levels: list[PriceLevel], depth: int=1) -> int:
        """Total quantity from top of book to a given depth."""
        return sum(pl.quantity for pl in levels[:depth])  # O(d)