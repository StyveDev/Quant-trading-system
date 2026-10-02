class StrategyRules:
    def __init__(self, ml_threshold=0.65):
        self.ml_threshold = ml_threshold

    def trend_direction(self, df):
        fast = df['ma_fast'].iloc[-1]
        slow = df['ma_slow'].iloc[-1]

        if fast > slow:
            return "up"
        elif fast < slow:
            return "down"
        return "neutral"

    
    def momentum_ok(self,df):
        rsi = df['rsi'].iloc[-1]
        return  45< rsi < 70
        

    def macd_confirmation(self, df):
        hist = df['macd_hist'].iloc[-1]
        return hist > 0  # up momentum

    def fractal_break(self, df):
        bull = df['fractal_up'].iloc[-1]
        bear = df['fractal_down'].iloc[-1]

        if bull == 1:
            return "bullish_break"
        if bear == 1:
            return "bearish_break"
        return None

    def ml_confirmation(self, prob: float):
        return prob >= self.ml_threshold
