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
    def initialize(self, cash_at_risk: float = 0.5):
        # Strategy settings
        self.symbol = "TSLA"
        self.sleeptime = "1D"
        self.window = 20  # Bollinger Band period
         # Bollinger Band width factor
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.TPSLRatio = 1.5
        self.slcoef = 1.1
        self.rsi_length = 16
        
    def get_data(self):
        df  = self.get_historical_prices(self.symbol, 500, "day").df
        df ["EMA_fast"]= ta.sma(df.close ,length=20)
        df ["EMA_slow"]= ta.sma(df.close, length=50)
        df['RSI']=ta.rsi(df.close, length=10)
        my_bbands = ta.bbands(df.close, length=15, std=1)
        df['ATR']=ta.atr(df.high, df.low, df.close, length=7)
        df=df.join(my_bbands)

        return(df)
        
    def ema_signal(self, df, current_candle, backcandles):
        df_slice = df.reset_index().copy()
        # Get the range of candles to consider
        start = max(0, current_candle - backcandles)
        end = current_candle
        relevant_rows = df_slice.iloc[start:end]

        # Check if all EMA_fast values are below EMA_slow values
        if all(relevant_rows["EMA_fast"] < relevant_rows["EMA_slow"]):
            return 1
        elif all(relevant_rows["EMA_fast"] > relevant_rows["EMA_slow"]):
            return 2
        else:
            return 0

        
    def total_signal(self, df, current_candle, backcandles):
        if (self.ema_signal(df, current_candle, backcandles)==2
            and df.close[current_candle]<=df['BBL_15_1.5'][current_candle]
                #and df.RSI[current_candle]<60
            ):
                return 2
        if (self.ema_signal(df, current_candle, backcandles)==1
            and df.close[current_candle]>=df['BBU_15_1.5'][current_candle]
                #and df.RSI[current_candle]>40
            ):
            
                return 1
        return 0
        
    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quantity
        
      
    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
      
            # Extract relevant data for the symbol
        
        
        # Calculate Bollinger Bands
        df = self.get_data()
        slatr = self.slcoef*df.ATR.iloc[-1]
        signal = self.total_signal(df, -1, 2)

      
        
        if cash > last_price:
        # Buy condition
           
            if signal==2:
                if self.last_trade == "sell":
                        self.sell_all()
                sl1 = self.df.close[-1] - slatr
                tp1 = self.df.close[-1] + slatr*self.TPSLRatio
            
                
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
                sl1 = self.data.close[-1] + slatr
                tp1 = self.data.close[-1] - slatr*self.TPSLRatio
            
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


backtesting_start =  datetime(2022,1,1)
backtesting_end =  datetime(2024,8,20)

# Initialize and run the strategy
if __name__ == '__main__':
    # Run the backtest
    #print(ALPACA_CREDS_PAPER)
    broker = Alpaca(ALPACA_CREDS_PAPER)
    strat = BollingerVWAPStrategy(name = "bollinger", broker=broker)
    strat.backtest(
        YahooDataBacktesting,
        backtesting_start,
        backtesting_end,
    )