import pyRofex

import simple_trading_bot.lib.test_module as tm
from simple_trading_bot.lib.pyrofex_init import init_pyrofex

init_pyrofex()

tm.TestClass()
instruments = ['DODic21', 'DONov21', 'DOAgo21', 'GGALFeb21', 'DOMar21', 'GGALAbr21', 'DOMay21', 'DOFeb21', 'DOJul21',
               'DOSep21', 'DOJun21', 'PAMPFeb21', 'DOOct21', 'DOAbr21', 'DOEne21']
entries = [pyRofex.MarketDataEntry.BIDS,
           pyRofex.MarketDataEntry.OFFERS,
           pyRofex.MarketDataEntry.LAST]

pyRofex.market_data_subscription(tickers=instruments,
                                 entries=entries)

