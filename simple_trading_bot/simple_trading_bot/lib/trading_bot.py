import time

from simple_trading_bot.lib.ir_expert import IRExpert
from simple_trading_bot.lib.market_data_feeds import RofexProxy, YfinanceMDFeed
from simple_trading_bot.lib.instrument_expert import InstrumentExpert
from simple_trading_bot.lib.data_update_watchman import DataUpdateWatchman
from simple_trading_bot.lib.trader import Trader


class IRTradingBot:

    def __init__(self, tickers):
        self._instrument_expert = InstrumentExpert(tickers)
        self._rofex_proxy = RofexProxy(self._instrument_expert)
        self._yfinance_md_feed = YfinanceMDFeed(self._instrument_expert, 1)
        self._data_update_watchman = DataUpdateWatchman(self._rofex_proxy, self._yfinance_md_feed)
        self._ir_expert = IRExpert(self._instrument_expert, self._rofex_proxy, self._yfinance_md_feed)
        self._trader = Trader(
            self._instrument_expert,
            self._ir_expert,
            self._rofex_proxy,
            self._yfinance_md_feed,
            self._data_update_watchman)

    def start(self):
        self._yfinance_md_feed.start_listening()
        self._rofex_proxy.start_listening()
        while True:
            if self._data_update_watchman.should_update():
                self._data_update_watchman.set_last_timestamp()
                start = time.time()
                self._ir_expert.update_rates()
                print(f'Update rates took {time.time() - start}')
                if self._ir_expert.ready():
                    self._trader.evaluate_and_trade()

