from queue import Queue
from threading import Thread
import time

from orderbook.orderbook import Orderbook
from orderbook.models import Order, CancelMessage, ExecutionMessage
from messages import MESSAGES, SYMBOLS

STOP_SENTINEL = object()


def producer(symbol: str, queue: Queue) -> None:
    """Imitates an exchange feed."""
    for msg in MESSAGES[symbol]:
        queue.put(msg)
        time.sleep(0.01)
    queue.put(STOP_SENTINEL)


def consumer(queue: Queue, order_book: Orderbook) -> None:
    """Per symbol consumer to route messages to the order book."""
    while True:
        msg = queue.get()
        if msg is STOP_SENTINEL:
            for q in order_book.subscriber_queues:  # propagate to every strategy
                q.put(STOP_SENTINEL)
            return
        if isinstance(msg, Order):
            order_book.on_order(msg)
        elif isinstance(msg, CancelMessage):
            order_book.on_cancel(msg)
        elif isinstance(msg, ExecutionMessage):
            order_book.on_execute(msg)


def quantity_strategy(symbol: str, event_queue: Queue, depth: int = 3) -> None:
    """Demonstrates API for quantity to a given depth."""
    while True:
        event = event_queue.get()
        if event is STOP_SENTINEL:
            return
        bids, asks = event
        bid_qty = Orderbook.get_quantity(bids, depth=depth)
        ask_qty = Orderbook.get_quantity(asks, depth=depth)
        print(f"[{symbol} qty @ depth {depth}] bid: {bid_qty}, ask: {ask_qty}")


def top_of_book_strategy(symbol: str, event_queue: Queue) -> None:
    """Demonstrates API for top of book price & quantity."""
    while True:
        event = event_queue.get()
        if event is STOP_SENTINEL:
            return
        bids, asks = event
        if not bids or not asks:  # book is one-sided
            continue
        print(f"[{symbol} tob] bid: {bids[0].quantity} @ ${bids[0].price}, ask: {asks[0].quantity} @ ${asks[0].price}")


def main():
    msg_queues: dict[str, Queue] = {symbol: Queue() for symbol in SYMBOLS}
    books: dict[str, Orderbook] = {symbol: Orderbook(symbol) for symbol in SYMBOLS}

    threads = []
    for symbol in SYMBOLS:
        queue = msg_queues[symbol]
        book = books[symbol]
        threads.extend([
            Thread(target=producer, args=(symbol, queue), daemon=True),
            Thread(target=consumer, args=(queue, book), daemon=True),
            Thread(target=quantity_strategy, args=(symbol, book.subscribe()), daemon=True),
            Thread(target=top_of_book_strategy, args=(symbol, book.subscribe()), daemon=True),
        ])

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print("Done")


if __name__ == "__main__":
    main()