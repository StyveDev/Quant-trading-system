import MetaTrader5 as mt5
import pandas as pd

TIMEFRAME_MAP= {
    "M1":mt5.TIMEFRAME_MN1,
    "M5":mt5.TIMEFRAME_M5,
    "M15":mt5.TIMEFRAME_M15,
    "H1":mt5.TIMEFRAME_H1,
    "H4":mt5.TIMEFRAME_H4,
    "D1":mt5.TIMEFRAME_D1
}


class MT5Loader:
    
    def __init__(self,symbol,timeframe,bars):
        self.symbol=symbol
        self.timeframe=timeframe
        self.bars=bars
    
    def connect(self):
        if not mt5.initialize():
            raise RuntimeError("MT5 initialization failed")
        print("MT5 connected")
    def load(self):
        tf = TIMEFRAME_MAP[self.timeframe]   
        rates=mt5.copy_rates_from_pos(
            self.symbol,
            tf,
            0,
            self.bars
        ) 
        df = pd.DataFrame(rates)
        
        df['datetime']=pd.to_datetime(df["datetime"])
        
        return df
    def shutdown(self):
        mt5.shutdown()
        