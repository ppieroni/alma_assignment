import pyRofex


pyRofex.initialize(user="pepieroni5584",
                   password="smstzM4#",
                   account="REM5584",
                   environment=pyRofex.Environment.REMARKET)

# First we define the handlers that will process the messages and exceptions.
def market_data_handler(message):
    print("Market Data Message Received: {0}".format(message))
def order_report_handler(message):
    print("Order Report Message Received: {0}".format(message))
def error_handler(message):
    print("Error Message Received: {0}".format(message))
def exception_handler(e):
    print("Exception Occurred: {0}".format(e.message))

# Initiate Websocket Connection
pyRofex.init_websocket_connection(market_data_handler=market_data_handler,
                                  order_report_handler=order_report_handler,
                                  error_handler=error_handler,
                                  exception_handler=exception_handler)

# Instruments list to subscribe
instruments = ["DOAbr21", "DOJun21"]
# Uses the MarketDataEntry enum to define the entries we want to subscribe to
entries = [pyRofex.MarketDataEntry.BIDS,
           pyRofex.MarketDataEntry.OFFERS,
           pyRofex.MarketDataEntry.LAST]

# Subscribes to receive market data messages **
pyRofex.market_data_subscription(tickers=instruments,
                                 entries=entries)