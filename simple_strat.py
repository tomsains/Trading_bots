from lumibot.strategies.strategy import Strategy
from lumibot.brokers.alpaca import Alpaca
import pandas as pd

class MovingAverageCrossover(Strategy):
    parameters = {
        "fast_period": 50,
        "slow_period": 200,
        "symbol": "AAPL",  # Example symbol
    }

    def initialize(self):
        self.position = None

    def on_trading_iteration(self):
        # Fetch the historical data needed for moving averages
        data = self.get_historical_data(
            self.parameters["symbol"], 
            self.parameters["slow_period"] + 1, 
            "1d"
        )

        # Calculate the moving averages
        fast_ma = data["close"].rolling(window=self.parameters["fast_period"]).mean().iloc[-1]
        slow_ma = data["close"].rolling(window=self.parameters["slow_period"]).mean().iloc[-1]

        # Buy if the fast moving average crosses above the slow moving average
        if fast_ma > slow_ma and not self.position:
            self.position = self.buy(self.parameters["symbol"], quantity=1)

        # Sell if the fast moving average crosses below the slow moving average
        elif fast_ma < slow_ma and self.position:
            self.sell(self.position)
            self.position = None

    def get_historical_data(self, symbol, lookback, interval):
        """
        Helper method to fetch historical data.
        """
        return self.broker.get_historical_data(symbol, lookback, interval)


  