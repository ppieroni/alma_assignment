## Simple IR Arbitrage Bot
### Overview
This module implements a _simple trading bot_ which looks for implicit 
rate arbitrage opportunities using futures and its underliers.
Futures market data is read from Rofex and spot market data from yahoo finance.
Then offered and taker implicit rates are computed for each contract to determine
if is there any buy/sell combination which gives instant profit. 
When any of these opportunities is present, orders are sent to a 
[simulated exchange](https://remarkets.primary.ventures/),
and relevant trade information is printed.
____
### Trading strategy
The trading strategy used here is pretty basic and requires the following steps:
1. For each future contract, the offered and taker implicit rate will be calculated.
1. Rates obtained from contracts with similar maturity will be compared looking for
low offered rates and high taker rates.
1. If any opportunity is found these positions will be taken:
    1. Buy long the contract with the minimum offered rate.
    1. Sell short its underlier, making this position neutral.
    1. Sell short the contract with the maximum taker rate.
    1. Buy long its underlier, making again the position neutral.
____
### Assumptions
Several assumptions has been made, such as:
* The transaction cost for each trade can be expressed as a constant,
  affecting the implicit rate difference directly. 
* There is no money market account available, so the only trade considered
  is among futures with similar maturity.
* The time to maturity for a contract is computed in days, starting _today_
  and including the maturity date. i.e. the number of _days to maturity_ on the maturity date is 1.
----
### Installation and Usage
This package has been developed for python 3.8 and its dependencies 
can be found in `<project root>/simple_trading_bot/requirements.txt`.

Installation can be made in three simple steps:
```shell
$ cd <project root>/simple_trading_bot/
$ pip install -r requirements.txt
$ pip insttall -e .
```

A simple script to launch the bot is provided in 
`<project root>/simple_trading_bot/simple_trading_bot/app/launch_simple_trading_bot.py` 
which basically contains something like:
```python
import simple_trading_bot.lib.trading_bot as tb

tickers = ['GGAL', 'YPFD', 'PAMP', 'DO']
spot_update_frequency = 1.
tb.IRArbitrageTradingBot(tickers, spot_update_frequency).launch()
```
____
### Design
The object design and its interactions is quite simple, 
based on few classes with clear responsibilities. Most of them are described here:

#### `IRArbitrageTradingBot`
As has been shown in the previous section, this class is the entry point to launch the process. 
It is in charge of instantiate all the classes described below, and ensure everything stays working.
Once the objects are created, its main responsibilities are:
* to keep the data retrieving going
* to launch the implicit rates calculation 
* perform trading every time the market data update happens.

#### `RofexProxy`
This is a proxy object for Rofex used to get the market data through websocket 
and also place and track orders using the rest api.
This object keeps track on the best bid and best ask for each of the contracts that will be traded.
It uses the [pyRofex](https://github.com/matbarofex/pyRofex) package in background for the connectivity tasks.

#### `YFinanceMDFeed`
Used to get the spot prices from Yahoo Finance on a regular basis,
that can be configured on instantiation. 
It uses the [yfinance](https://github.com/ranaroussi/yfinance) 
package to interact with the data server.
As in the `RofexProxy`, the data will be marked as updated only when a change in the prices took place.

#### `DataUpdateWatchman`
The main responsibility of this class is to keep track of the data reading,
used as a reference to know whether new data has arrived or not.
This can be achieved by setting up a landmark each time data will be read 
(using `set_last_processed_timestamp`) and through the `should_update` method.

#### `IRExpert`
This class is used to compute and provide the implicit rate for each contract.
The method `update_rates` will be called every time there is change either in the 
future prices, or in the spot prices, updating the values.
The rates are computed using daily compounding, and an Actual/365 day count convention.

#### `IRPrinter`
Helper class intended to print the rates computed by the `IRExpert`, 
ordered in such way it will be easy to spot arbitrage opportunities for each tenure.
As an example:
```
Last Updated Rates:
+----------------------------+----------------------------+
|           Feb21            |           Abr21            |
|----------------------------+----------------------------|
| GGALFeb21    ->   0.297485 | ************ -> ********** |
| PAMPFeb21    ->   0.417927 | ************ -> ********** |
| DOFeb21      ->   0.441218 | GGALAbr21    ->   0.355318 |
| YPFDFeb21    ->   0.467888 | DOAbr21      ->   0.468321 |
| ++++++++++++++++++++++++++ | ++++++++++++++++++++++++++ |
| DOFeb21      ->   0.449649 | DOAbr21      ->   0.479019 |
| PAMPFeb21    ->   0.516258 | ************ -> ********** |
| GGALFeb21    ->   0.522267 | ************ -> ********** |
| YPFDFeb21    ->   0.562362 | ************ -> ********** |
+----------------------------+----------------------------+
```
Each column groups the rates with the same tenure ordered from lower to higher. 
The upper/lower block shows the taker/offered rates respectively, 
so the rates closer to `+` line are the max taker rate, and the min offered rate.

#### `Trader`
Once the implicit rates are updated this class is in charge of looking for arbitrage 
opportunities and sending the orders to the market (see `evaluate_and_trade_single_maturity`).
Also, every time a trade opportunity has been detected, and a suitable trade can be performed,
it prints a summary which will looks similar to:

```
--- Trade Info For Tenure Feb21 ---
Rate long side:
Buy:      DOFeb21      ->        7 @ 90.33
Sell:     DO           ->   7000.0 @ 87.70
Imp Rate: 0.449649
Traded amount: 613899.98
Order reception info:   {'status': 'OK', 'order': {'clientId': '350836323223783', 'proprietary': 'PBCP'}}
Order execution status: FILLED
---
Rate short side:
Sell:     YPFDFeb21    ->        9 @ 658.90
Buy:      YPFD         ->    900.0 @ 638.95
Imp Rate: 0.467888
Traded amount: 575055.01
Order reception info:   {'status': 'OK', 'order': {'clientId': '350836324223784', 'proprietary': 'PBCP'}}
Order execution status: FILLED
--------------------------------------------
```

#### Testing
Some unit test for `IRExpert` and `Trader` classes can be found in `<project root>/simple_trading_bot/simple_trading_bot` 

### Known issues & further improvements
Here we list some known issues and potential future improvements without any specific order. 
They were not tackled mostly because some lower hanging fruits were found. 

#### Technical
- Every time a price is updated all the implicit rates are calculated. 
  A simple optimization here could be to calculate only the rates which depends on the changed price.
  This optimization was left behind because the amount of updates is relatively low when compared with 
  the time the calculus takes.
- No further track of the order status is made because it exceeds the assignment scope.
  The next step to make this bot more functional should be following the orders placed asynchronously
  and performing some tracking on the inventory (which could be key to computing exposures 
  and determining the trade sizes).
- Exception handling is fairly basic across the library. 
  Some specific exceptions could be included to contemplate boundary cases but 
  this would require some more time to find such cases.
- A simple change to improve the readability of the program output would be using the `logging` library. 
- When the most profitable opportunity is not tradeable* there should be a fallback 
  to look for other less but still profitable opportunities.
  
'* i.e. 2 contracts of `GGALAbr21` vs 1 contract of `DOAbr21`,
which will imply a very unbalanced trade due to the contract sizes

####Financial
- The day count to maturity is calculated in days in a very simple way (number of days until maturity + 1). 
  This approach has issues when maturity is close, and when the compared contracts 
  do not have exactly the same maturity date.
- Transaction costs are assumed as a constant cost. A more realistic approach 
  is key to spot real opportunities. 
- It is assumed that there is no money market account available, making transactions 
  between different tenures not viable.
  Including this possibility would allow the bot to find even more opportunities.
- Futures with similar maturity (i.e. `GGALFeb21` and `DOFeb21`) are supposed to 
  finish in the same exact date regarding the trade, but the implicit rates are computed using 
  the correct time to maturity.

