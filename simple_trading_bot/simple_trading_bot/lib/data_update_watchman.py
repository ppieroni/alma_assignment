

class DataUpdateWatchman:

    def __init__(self, rofex_proxy, yfinance_md_feed):
        self._rofex_proxy = rofex_proxy
        self._yfinance_md_feed = yfinance_md_feed
        self._last_proc_timestamp = 0.

    def set_last_timestamp(self):
        self._last_proc_timestamp = max(
            self._rofex_proxy.last_update_timestamp(),
            self._yfinance_md_feed.last_update_timestamp())

    def should_update(self):
        return (self._last_proc_timestamp < self._rofex_proxy.last_update_timestamp() or
                self._last_proc_timestamp < self._yfinance_md_feed.last_update_timestamp())
