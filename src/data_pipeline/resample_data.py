class Resampler:
    @staticmethod
    def resample(df,timeframe="4H"):
        df =df.copy()
        df= df.set_index("datetime")
        ohlc={
            "open":"first",
            "high":"max",
            "low":"min",
            "close":"last",
            "volume":"sum",
        }
        resampled=df.resample(timeframe).agg(ohlc)
        resampled=resampled.dropna()
        return resampled.reset_index()
    