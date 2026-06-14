# Orderbook

Order book with a threaded producer/consumer pipeline for multiple symbols.

Each symbol runs its own producer, consumer, and strategy threads. 

Orderbook stores each side of the book in a [`SortedDict`](https://grantjenks.com/docs/sortedcontainers/sorteddict.html) keyed on price. 

Strategies subscribe to order book updates via queues and receive a snapshot of price levels on every change.

## Layout

```
orderbook/          # library
    orderbook.py    # Orderbook + notify decorator
    models.py       # Order / CancelMessage / ExecutionMessage / PriceLevel
main.py             # demo: wires producers, consumers, strategies
messages.py         # demo message data
```

## Run

```sh
uv run main.py
```

## Time complexity

`k` = number of price levels, `d` = depth traversed from top of book.

| Operation          | Complexity |
| ------------------ | ---------- |
| `on_order`         | O(log k)   |
| `on_cancel`        | O(log k)   |
| `on_execute`       | O(log k)   |
| `get_price_levels` | O(k)       |
| `get_quantity`     | O(d)       |
| `notify_subscribers`| O(d) |
