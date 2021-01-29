

class IRExpert:
    DAYS_IN_A_YEAR = 365

    def __init__(self, instrument_expert, rofex_proxy, yfinance_md_feed):
        self._futures_by_underlier_ticker = instrument_expert.rofex_instrument_by_underlier()
        self._rofex_proxy = rofex_proxy
        self._yfinance_md_feed = yfinance_md_feed
        self._taker_rates = {}
        self._offered_rates = {}

    def update_rates(self):
        underlier_prices = self._yfinance_md_feed.last_prices()
        future_bids = self._rofex_proxy.bids()
        future_asks = self._rofex_proxy.asks()
        self._taker_rates = {}
        self._offered_rates = {}
        for ticker, underlier_price in underlier_prices.items():
            for future in self._futures_by_underlier_ticker[ticker]:
                future_ticker = future.ticker()
                days_to_maturity = future.days_to_maturity()
                if future_ticker in future_bids:
                    self._taker_rates[future_ticker] = self._implicit_rate(
                        future_bids[future_ticker].price,
                        underlier_price,
                        days_to_maturity)
                if future_ticker in future_asks:
                    self._offered_rates[future_ticker] = self._implicit_rate(
                        future_asks[future_ticker].price,
                        underlier_price,
                        days_to_maturity)

    def max_taker_rate(self):
        return max(self._taker_rates.items(), key=lambda each: each[1])

    def min_offered_rate(self):
        return min(self._offered_rates.items(), key=lambda each: each[1])

    def ready(self):
        return self._taker_rates and self._offered_rates

    def _implicit_rate(self, maturity_price, current_price, days_to_maturity):
        """Anualized implicit rate computed using Actual/DAYS_IN_A_YEAR day count convention and daily compounding"""
        return ((maturity_price / current_price) ** (1 / days_to_maturity) - 1) * self.DAYS_IN_A_YEAR



