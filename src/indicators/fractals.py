import pandas as pd

class FractalsIndicator:
    def calculate(self, df: pd.DataFrame):
        highs = df['high']
        lows = df['low']

        bullish = (lows.shift(2) > lows.shift(1)) & \
                  (lows.shift(1) > lows) & \
                  (lows.shift(1) < lows.shift(-1)) & \
                  (lows.shift(2) < lows.shift(-2))

        bearish = (highs.shift(2) < highs.shift(1)) & \
                  (highs.shift(1) < highs) & \
                  (highs.shift(1) > highs.shift(-1)) & \
                  (highs.shift(2) > highs.shift(-2))

        return bullish.astype(int), bearish.astype(int)
