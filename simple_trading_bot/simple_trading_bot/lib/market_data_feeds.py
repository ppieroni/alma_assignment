import threading
import time
from collections import defaultdict
from pprint import pprint as pp

import pyRofex
import yfinance

import simple_trading_bot.lib.pyrofex_wrapper as prw


FLOAT_LIMIT = 1e-4


class MarketDataFeed:

    def __init__(self):
        self._last_update_timestamp = 0.

    def last_update_timestamp(self):
        return self._last_update_timestamp

    def _update_last_timestamp(self):
        self._last_update_timestamp = time.time()


class YfinanceMDFeed(MarketDataFeed):

    def __init__(self, instrument_expert, update_frequency):
        super().__init__()
        self._tickers = instrument_expert.yfinance_tickers()
        self._inverse_ticker_map = instrument_expert.inverse_yfinance_tickers_map()
        self._update_frequency = update_frequency
        self._listening_thread = threading.Thread(target=self._update_prices)
        self._prices = {}

    def start_listening(self):
        self._listening_thread.start()

    def last_prices(self):
        return self._prices.copy()

    def _update_prices(self):
        while True:
            data = yfinance.download(
                tickers=self._tickers,
                period='1d',
                interval='1d',
                progress=False)
            start = time.time()
            prices = data['Close'].to_dict(orient='records')[0]
            print(f'Updating spot prices {prices}')
            if any((price - self._prices.get(self._inverse_ticker_map[ticker], 0.) > FLOAT_LIMIT)
                   for ticker, price in prices.items()):
                self._prices = {self._inverse_ticker_map[ticker]: price for ticker, price in prices.items()}
                self._update_last_timestamp()
                print(f'updated {self._prices}')
            time.sleep(self._update_frequency)


class RofexProxy(MarketDataFeed):
    DATA_ENTRIES = [
        pyRofex.MarketDataEntry.BIDS,
        pyRofex.MarketDataEntry.OFFERS]

    def __init__(self, instrument_expert):
        super().__init__()
        self._futures_ticker = instrument_expert.futures_ticker()
        self._pyrofex_wrapper = prw.PyRofexWrapper()
        self._bids = defaultdict(dict)
        self._asks = defaultdict(dict)
        self._pyrofex_wrapper.init_websocket_connection(
            market_data_handler=self._market_data_handler,
            order_report_handler=self._order_report_handler,
            error_handler=self._error_handler,
            exception_handler=self._exception_handler)

    def __str__(self):
        repr_str = ''
        all_tickers = set(self._bids.keys()).union(set(self._asks.keys()))
        for ticker in all_tickers:
            repr_str += (f'{ticker}: '
                         f'{self._bids[ticker].get(pyRofex.MarketDataEntry.BIDS.value, "-")}'
                         f'{self._asks[ticker].get(pyRofex.MarketDataEntry.OFFERS.value, "-")}')
        return repr_str

    def start_listening(self):
        self._pyrofex_wrapper.market_data_subscription(
            tickers=self._futures_ticker,
            entries=self.DATA_ENTRIES)
        self._pyrofex_wrapper.order_report_subscription()

    def asks(self):
        return self._asks.copy()

    def bids(self):
        return self._bids.copy()

    def place_order(self, *args, **kwargs):
        return pyRofex.send_order(*args, **kwargs)

    def _market_data_handler(self, message):
        print("Market Data Message Received: {0}".format(message))
        ticker = message['instrumentId']['symbol']
        market_data = message['marketData']
        if market_data[pyRofex.MarketDataEntry.OFFERS.value]:
            self._asks[ticker] = market_data[pyRofex.MarketDataEntry.OFFERS.value][0]
        if market_data[pyRofex.MarketDataEntry.BIDS.value]:
            self._bids[ticker] = market_data[pyRofex.MarketDataEntry.BIDS.value][0]
        self._update_last_timestamp()

    def _order_report_handler(self, message):
        print("Order Report Message Received: {0}".format(message))

    def _error_handler(self, message):
        print("Error Message Received: {0}".format(message))

    def _exception_handler(self, e):
        print("Exception Occurred: {0}".format(e.message))


