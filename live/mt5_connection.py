# mt5_connection.py
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta


class MT5Connection:
    def __init__(self, symbol="EURUSD", timeframe=mt5.TIMEFRAME_M15, days=365):
        self.symbol = symbol
        self.timeframe = timeframe
        self.start = datetime.now() - timedelta(days=days)
        self.end = datetime.now()
        self.initialize()

    def initialize(self):
        if not mt5.initialize():
            print("MT5 initialization failed")
            mt5.shutdown()
            return False
        print("MT5 initialized successfully")
        return True

    def get_historical_data(self):
        rates = mt5.copy_rates_range(self.symbol, self.timeframe, self.start, self.end)
        df = pd.DataFrame(rates)
        # df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
        # df.set_index('time', inplace=True)
        return df


if __name__ == "__main__":
    connection = MT5Connection()
    df = connection.get_historical_data()
    print(df.head())
