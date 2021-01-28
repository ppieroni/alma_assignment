from collections import namedtuple

import pyRofex

import simple_trading_bot.conf.transaction_costs as tc


TradeInfo = namedtuple('TradeInfo', '')


class Trader:
    def __init__(
            self,
            instrument_expert,
            ir_expert,
            rofex_proxy,
            yfinance_md_feed,
            data_update_watchman):
        self._futures_by_ticker = instrument_expert.rofex_instruments_by_ticker()
        self._ir_expert = ir_expert
        self._rofex_proxy = rofex_proxy
        self._yfinance_md_feed = yfinance_md_feed
        self._data_update_watchman = data_update_watchman


    def evaluate_and_trade(self):
        ticker_to_sell, max_taker_rate = self._ir_expert.max_taker_rate()
        ticker_to_buy, min_offered_rate = self._ir_expert.min_offered_rate()
        if not max_taker_rate - min_offered_rate > tc.TRANSACITON_COST:
            return

        future_asks = self._rofex_proxy.asks()
        future_bids = self._rofex_proxy.bids()
        future_to_buy = self._futures_by_ticker[ticker_to_buy]
        future_to_sell = self._futures_by_ticker[ticker_to_sell]
        underlier_to_sell = future_to_buy.underlier_ticker()
        underlier_to_buy = future_to_sell.underlier_ticker()

        available_buy_size = future_asks[ticker_to_buy]['size']
        available_sell_size = future_bids[ticker_to_sell]['size']
        amount_to_trade = min(
            available_buy_size * future_to_buy.contract_size(),
            available_sell_size * future_to_sell.contract_size())
        buy_size = int(amount_to_trade / future_to_buy.contract_size())
        sell_size = int(amount_to_trade / future_to_sell.contract_size())
        buy_price = future_asks[ticker_to_buy]['price']
        sell_price = future_bids[ticker_to_sell]['price']

        if not self._data_update_watchman.should_update():
            buy_order = self._rofex_proxy.place_order(
                ticker=ticker_to_buy,
                side=pyRofex.Side.BUY,
                size=amount_to_trade,
                price=buy_price,
                order_type=pyRofex.OrderType.LIMIT)

            sell_order = self._rofex_proxy.place_order(
                ticker=ticker_to_sell,
                side=pyRofex.Side.SELL,
                size=amount_to_trade,
                price=sell_price,
                order_type=pyRofex.OrderType.LIMIT)
