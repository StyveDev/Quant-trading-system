import pandas as pd

class EMAIndicator:
    def __init__(self, period: int):
        self.period = period

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        return df['close'].ewm(span=self.period, adjust=False).mean()
