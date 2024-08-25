import pandas as pd
import pandas_ta as ta
import numpy as np
from lumibot.backtesting import YahooDataBacktesting
from lumibot.traders import Trader
from lumibot.strategies.strategy import Strategy
from lumibot.brokers.alpaca import Alpaca
from Alpaca_creds import ALPACA_CREDS_PAPER, BASE_URL
from datetime import datetime


class BollingerVWAPStrategy(Strategy):
    def initialize(self, cash_at_risk = 0.5, symbol="PLTR", TPSLRatio=1.5, ema_fast = 20, ema_slow=50):
        # Strategy settings
        self.symbol = symbol
        self.sleeptime = "1D"
        self.window = 20  # Bollinger Band period
         # Bollinger Band width factor
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.TPSLRatio = TPSLRatio
        self.slcoef = 1.1
        self.rsi_length = 16
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        
    def get_data(self):
        df  = self.get_historical_prices(self.symbol, 1000, "day").df
        df ["EMA_fast"]= ta.sma(df.close ,length=self.ema_fast)
        df ["EMA_slow"]= ta.sma(df.close, length=self.ema_slow)
        df['ATR']=ta.atr(df.high, df.low, df.close, length=7)
        return(df)
        
    def ema_signal(self, df, back_candles = 5):
        df_slice = df.reset_index().copy()
        # Get the range of candles to consider
       
        relevant_rows = df_slice.iloc[-1]
        previous_rows =  df_slice.iloc[-back_candles:-2]

        # Check if all EMA_fast values are below EMA_slow values
        if (relevant_rows["EMA_fast"] < relevant_rows["EMA_slow"]) and all(previous_rows["EMA_fast"] > previous_rows["EMA_slow"]):
            return 1
        elif (relevant_rows["EMA_fast"] > relevant_rows["EMA_slow"]) and all(previous_rows["EMA_fast"] < previous_rows["EMA_slow"]):
            return 2
        else:
            return 0

        
    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk /last_price, 0)
        return cash, last_price, quantity
        
      
    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
      
            # Extract relevant data for the symbol
        
        
        # Calculate Bollinger Bands
        df = self.get_data()
        slatr = self.slcoef*df.ATR.iloc[-1]
        signal = self.ema_signal(df)

      
        
        if cash > last_price:
        # Buy condition
           
            if signal==2:
                if self.last_trade == "sell":
                        self.sell_all()
                sl1 = df.close.iloc[-1] - slatr
                tp1 = df.close.iloc[-1] + slatr*self.TPSLRatio
            
                
                order = self.create_order(
                        self.symbol,
                        quantity,
                        "buy",
                        type="bracket",
                        take_profit_price=tp1,
                        stop_loss_price=sl1,
                    )
                self.submit_order(order)
                self.last_trade ="buy"

            # Sell condition
            elif signal==1:   
                if self.last_trade == "buy":   
                    self.sell_all()   
                sl1 = df.close.iloc[-1] + slatr
                tp1 = df.close.iloc[-1] - slatr*self.TPSLRatio
            
                order = self.create_order(
                        self.symbol,
                        quantity,
                        "sell",
                        type="bracket",
                        take_profit_price=tp1,
                        stop_loss_price=sl1,
                    )
                self.submit_order(order)
                self.last_trade = "sell"


backtesting_start =  datetime(2023,1,1)
backtesting_end =  datetime(2024,8,24)

# Initialize and run the strategy
if __name__ == '__main__':
    # Run the backtest
    #print(ALPACA_CREDS_PAPER)
    broker = Alpaca(ALPACA_CREDS_PAPER)
    strat = BollingerVWAPStrategy(name = "moving", broker=broker)
    strat.backtest(
        YahooDataBacktesting,
        backtesting_start,
        backtesting_end,
        parameters={"symbol": "TSLA", "TPSLRatio": 1.5}
        
    )