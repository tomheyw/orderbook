from orderbook.models import Order, CancelMessage, ExecutionMessage, Side


SYMBOLS = ["AAPL", "MSFT"]

MESSAGES: dict[str, list] = {
    "AAPL": [
        Order(order_id=1,  symbol="AAPL", side=Side.BID, price=150.00, quantity=100),
        Order(order_id=2,  symbol="AAPL", side=Side.BID, price=149.50, quantity=200),
        Order(order_id=3,  symbol="AAPL", side=Side.ASK, price=151.00, quantity=150),
        Order(order_id=4,  symbol="AAPL", side=Side.ASK, price=151.50, quantity=100),
        Order(order_id=5,  symbol="AAPL", side=Side.BID, price=150.25, quantity=300),
        CancelMessage(order_id=2,  symbol="AAPL"),
        Order(order_id=6,  symbol="AAPL", side=Side.ASK, price=152.00, quantity=200),
        ExecutionMessage(order_id=3,  symbol="AAPL", quantity=150),
        Order(order_id=7,  symbol="AAPL", side=Side.BID, price=149.00, quantity=50),
        ExecutionMessage(order_id=5,  symbol="AAPL", quantity=100),
    ],
    "MSFT": [
        Order(order_id=8,  symbol="MSFT", side=Side.ASK, price=420.00, quantity=80),
        Order(order_id=9,  symbol="MSFT", side=Side.ASK, price=420.50, quantity=120),
        Order(order_id=10, symbol="MSFT", side=Side.BID, price=419.00, quantity=200),
        Order(order_id=11, symbol="MSFT", side=Side.BID, price=418.50, quantity=150),
        ExecutionMessage(order_id=8,  symbol="MSFT", quantity=80),
        Order(order_id=12, symbol="MSFT", side=Side.ASK, price=421.00, quantity=100),
        CancelMessage(order_id=11, symbol="MSFT"),
        Order(order_id=13, symbol="MSFT", side=Side.BID, price=419.50, quantity=250),
        ExecutionMessage(order_id=9,  symbol="MSFT", quantity=60),
        Order(order_id=14, symbol="MSFT", side=Side.ASK, price=420.75, quantity=90),
    ],
}