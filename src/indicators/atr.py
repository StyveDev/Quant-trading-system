import pandas as pd

class ATRIndicator:
    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()

        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(self.period).mean()

        return atr
