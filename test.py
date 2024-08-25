from lumibot.brokers import Alpaca
from simple_strat import MovingAverageCrossover
from Alpaca_creds import ALPACA_CREDS_PAPER
from lumibot.backtesting import YahooDataBacktesting
from datetime import datetime


if __name__ == '__main__':
    # Run the backtest
    start_date = datetime(2024, 3, 22)
    end_date = datetime.today()
    #print(ALPACA_CREDS_PAPER)
    broker = Alpaca(ALPACA_CREDS_PAPER)
    strat = MovingAverageCrossover(name = "buy_and_hold", broker=broker, parameters={})
    strat.backtest(
        YahooDataBacktesting,
        start_date,
        end_date,
    )