import pyRofex
from simple_trading_bot.lib.instrument_expert import InstrumentExpert


pyRofex.initialize(user="pepieroni5584",
                   password="smstzM4#",
                   account="REM5584")#,
                   # environment=pyRofex.Environment.REMARKET)

def market_data_handler(message):
    print("Market Data Message Received: {0}".format(message))
def order_report_handler(message):
    print("Order Report Message Received: {0}".format(message))
def error_handler(message):
    print("Error Message Received: {0}".format(message))
def exception_handler(e):
    print("Exception Occurred: {0}".format(e.message))

pyRofex.init_websocket_connection(market_data_handler=market_data_handler,
                                  order_report_handler=order_report_handler,
                                  error_handler=error_handler,
                                  exception_handler=exception_handler)

instruments = ['DODic21', 'DONov21', 'DOAgo21', 'DOMar21', 'DOMay21', 'DOFeb21', 'DOJul21', 'DOSep21', 'DOJun21',
               'DOOct21', 'DOAbr21', 'DOEne21']

# ie = InstrumentExpert(['GGAL', 'DO', 'PAMP', 'YPF'])
# print(ie.futures_ticker())
# instruments = ie.futures_ticker()
# ['DODic21', 'DONov21', 'DOAgo21', 'GGALFeb21', 'DOMar21', 'GGALAbr21', 'DOMay21', 'DOFeb21', 'DOJul21',
#                'DOSep21', 'DOJun21', 'PAMPFeb21', 'DOOct21', 'DOAbr21', 'DOEne21']

entries = [pyRofex.MarketDataEntry.BIDS,
           pyRofex.MarketDataEntry.OFFERS,
           pyRofex.MarketDataEntry.LAST]

pyRofex.market_data_subscription(tickers=instruments,
                                 entries=entries)
