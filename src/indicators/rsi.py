import pandas as pd

class RSIIndicator:
    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.period).mean()

        rs = gain / loss
        return 100 - (100 / (1 + rs))
