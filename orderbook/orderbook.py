"""
Orderbook time complexities
    on_order: O(log k)
    on_cancel: O(log k)
    on_execute: O(log k)
    get_price_levels: O(d)
    get_quantity: O(d)
    notify_subscribers: O(d)

Where
    k: no. of price levels
    d: depth of book (price levels traversed from top of book)
"""

from sortedcontainers import SortedDict
from queue import Queue

from .models import CancelMessage, ExecutionMessage, Side, Order, PriceLevel

type Book = SortedDict[float, int]


def notify_subscribers(func):
    def wrapper(self: Orderbook, *args, **kwargs):
        """Notify subscribers with a snapshot of the orderbook."""
        result = func(self, *args, **kwargs)
        if self.subscriber_queues:
            depth = self.max_subscription_depth
            snapshot = (
                Orderbook.get_price_levels(self.bid_book, depth),
                Orderbook.get_price_levels(self.ask_book, depth),
            )
            for q in self.subscriber_queues:
                q.put(snapshot)
        return result
    return wrapper


class Orderbook:
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.orders = {}
        self.bid_book: Book = SortedDict(lambda x: -x)  # desc
        self.ask_book: Book = SortedDict()  # asc
        self.subscriber_queues: list[Queue] = []
        self.max_subscription_depth: int = 1

    @notify_subscribers
    def on_order(self, msg: Order) -> None:
        self.orders[msg.order_id] = msg  # O(1)
        book = self.bid_book if msg.side == Side.BID else self.ask_book
        qty = book.get(msg.price, 0)  # O(1)
        book[msg.price] = qty + msg.quantity  # insert: O(log k)

    @notify_subscribers
    def on_cancel(self, msg: CancelMessage) -> None:
        order = self.orders[msg.order_id]  # O(1)
        book = self.bid_book if order.side == Side.BID else self.ask_book
        book[order.price] -= order.quantity  # O(1)
        if book[order.price] == 0:  # clean empty price-level
            del book[order.price]  # O(log k)

        # update orders dict
        del self.orders[msg.order_id]  # O(1)

    @notify_subscribers
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
    def get_price_levels(book: Book, depth: int=1) -> list[PriceLevel]:
        """Snapshot of price levels to a given depth for bid/ask side."""
        i = 1
        price_levels = []
        for price, quantity in book.items():
            if i > depth:
                break
            price_levels.append(PriceLevel(price=price, quantity=quantity))
            i += 1
        return price_levels
    
    @staticmethod
    def get_quantity(levels: list[PriceLevel], depth: int=1) -> int:
        """Total quantity from top of book to a given depth."""
        return sum(pl.quantity for pl in levels[:depth])  # O(d)
    
    def subscribe(self, max_depth: int=1) -> Queue:
        """Each subscriber gets its own event queue."""
        self.max_subscription_depth = max(self.max_subscription_depth, max_depth)
        q = Queue()
        self.subscriber_queues.append(q)
        return q