from datetime import datetime

class StrategyFilters:
    def __init__(self):
        self.london_start = 9
        self.london_end = 17
        self.ny_start = 15
        self.ny_end = 20

    def session_filter(self):
        hour = datetime.now().hour
        
        
        if self.ny_start <= hour <= self.ny_end:
            return True
        return False

    def volatility_filter(self, df):
        atr = df['atr'].iloc[-1]
        return atr > df['atr'].rolling(50).mean().iloc[-1]

    def spread_filter(self, spread):
        return spread < 20  # 2 pips max
