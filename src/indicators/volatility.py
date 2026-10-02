import pandas as pd

class VolatilityIndicator:
    def __init__(self, period: int = 20):
        self.period = period

    def std_dev(self, df: pd.DataFrame) -> pd.Series:
        return df['close'].rolling(self.period).std()

    def percent_volatility(self, df: pd.DataFrame) -> pd.Series:
        return (df['close'].rolling(self.period).std() / df['close']) * 100
