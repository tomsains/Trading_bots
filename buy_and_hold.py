from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime 
from alpaca_trade_api import REST 


class BuyAndHold(Strategy):
    def initialize(self, stock = "AAPL"):
        self.stock = stock
        self.sleeptime("24H")
    
    def on_trading_iteration(self):
       
        if self.first_iteration:
            aapl_price = self.get_last_price(self.stock)
            quantity = self.portfolio_value // aapl_price
            order = self.create_order(self.stock, quantity, "buy")
            self.submit_order(order)
       
       



    

# Pick the dates that you want to start and end your backtest
backtesting_start = datetime(2023, 11, 1)
backtesting_end = datetime.now()


if __name__ == '__main__':
    # Run the backtest
    strat = BuyAndHold(name = "buy_and_hold", broker=None, parameters={})
    strat.backtest(
        YahooDataBacktesting,
        backtesting_start,
        backtesting_end,
    )