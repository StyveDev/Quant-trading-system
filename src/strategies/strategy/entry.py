class EntryLogic:
    def __init__(self, rules, filters):
        self.rules = rules
        self.filters = filters

    def check_buy(self, df, spread):
        #if not self.filters.session_filter():
         #   return False
    
        #if not self.filters.spread_filter(spread):
          #  return False

        if self.rules.trend_direction(df) != "up":
            return False
        
        if not self.rules.momentum_ok(df):
            return False

       # if not self.rules.macd_confirmation(df):
          #  return False
        if self.rules.fractal_break(df) != "bullish_break":
            return False  

       # if not self.rules.ml_confirmation(ml_prob):
         #  return False

        if self.rules.fractal_break(df) != "bullish_break":
            return False

        return True

    def check_sell(self, df, spread):
       # if not self.filters.session_filter():
         #   return False

      #  if not self.filters.spread_filter(spread):
           # return False

        

        if self.rules.trend_direction(df) != "down":
            return False
        if not self.rules.momentum_ok(df):
            return False
       # if not self.rules.ml_confirmation(ml_prob):
        #    return False

        if self.rules.fractal_break(df) != "bearish_break":
            return False

        return True
