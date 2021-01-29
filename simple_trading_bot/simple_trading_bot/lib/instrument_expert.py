import re
import datetime as dt
from dateutil.parser import parse
from collections import defaultdict

import simple_trading_bot.lib.exceptions as exc
import simple_trading_bot.lib.pyrofex_wrapper as prw


class Future:

    def __init__(self, ticker, maturity_date, underlier_ticker, contract_size):
        self._ticker = ticker
        self._maturity_date = maturity_date
        self._underlier_ticker = underlier_ticker
        self._contract_size = contract_size

    def __repr__(self):
        return f'{self._ticker}: [{self._underlier_ticker} - {self._maturity_date} - {self._contract_size}]'

    def ticker(self):
        return self._ticker

    def maturity_date(self):
        return self._maturity_date

    def underlier_ticker(self):
        return self._underlier_ticker

    def contract_size(self):
        return self._contract_size

    def days_to_maturity(self, start_date=None):
        start_date = start_date or dt.datetime.now()
        delta = self._maturity_date.date() - start_date.date()
        if delta.days <= 0:
            raise exc.ExpiredInstrument(self)
        return delta.days


class InstrumentExpert:

    def __init__(self, tickers):
        self._tickers = tickers
        self._rofex_instrument_by_underlier = defaultdict(list)
        self._yfinance_tickers_map = {ticker: self._yfinance_ticker(ticker) for ticker in tickers}
        self._inverse_yfinance_tickers_map = {v: k for k, v in self._yfinance_tickers_map.items()}
        self._rofex_instruments_by_ticker = dict()
        self._load_rofex_instruments()

    def futures_ticker(self):
        return list(self._rofex_instruments_by_ticker.keys())

    def yfinance_tickers(self):
        return list(self._yfinance_tickers_map.values())

    def inverse_yfinance_tickers_map(self):
        return self._inverse_yfinance_tickers_map.copy()

    def rofex_instrument_by_underlier(self):
        return self._rofex_instrument_by_underlier.copy()

    def rofex_instruments_by_ticker(self):
        return self._rofex_instruments_by_ticker.copy()

    def _load_rofex_instruments(self):
        futures_regexps = {ticker: re.compile(f'^{ticker}[A-Z][a-z][a-z]2.$') for ticker in self._tickers}
        rest_instruments = prw.PyRofexWrapper().get_detailed_instruments()
        for instrument in rest_instruments['instruments']:
            for ticker, regexp in futures_regexps.items():
                if regexp.match(instrument['instrumentId']['symbol']):
                    rofex_ticker = instrument['instrumentId']['symbol']
                    maturity_date = parse(instrument['maturityDate'])
                    contract_size = instrument['contractMultiplier']
                    future = Future(rofex_ticker, maturity_date, ticker, contract_size)
                    self._rofex_instrument_by_underlier[ticker].append(future)
                    self._rofex_instruments_by_ticker[rofex_ticker] = future

    @staticmethod
    def _yfinance_ticker(ticker):
        if ticker == 'DO':
            return 'ARS=X'
        return ticker + '.BA'
