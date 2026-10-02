# data/feature_engineering.py

import pandas as pd

import os


class FeatureEngineer:
        
        def add_features(df):
    
         df=df.copy
  
         df["ema_20"] = df['close'].ewm(span=9).mean()
         df["ema_50"] = df['close'].ewm(span=50).mean()
         delta = df['close'].diff()
         gain = (delta.where(delta > 0, 0)).rolling(14).mean()
         loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
         rs = gain / loss
         rsi=100 - (100 / (1 + rs))
    
         df["rsi"] = rsi
    

         slow=26
         fast=12
         signal=9
         ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
         ema_slow = df["close"].ewm(span=slow, adjust=False).mean()

         macd_line = ema_fast - ema_slow
         signal_line = macd_line.ewm(span=signal, adjust=False).mean()
         histogram = macd_line - signal_line
         df["macd"] = macd_line
         df["macd_signal"] = signal_line
         df["macd_hist"]=histogram
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

         f_up =bullish
         f_down = bearish
         df["fractal_up"] = f_up
         df["fractal_down"] = f_down
         high_low = df['high'] - df['low']
         high_close = (df['high'] - df['close'].shift()).abs()
         low_close = (df['low'] - df['close'].shift()).abs()
         period=14
    
         tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
         atr = tr.rolling(period).mean()
         df["atr"] = atr
         df['bull'] = (df['close'] < df['open']).astype(int)
         perd=20
         df["volatility"] = (df['close'].rolling(perd).std() / df['close']) * 100
         df = df.dropna()
         df = df.to_csv(output_path,index=False)
         return df

  
  