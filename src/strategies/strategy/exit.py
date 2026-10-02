class ExitLogic:
    def __init__(self):
        pass

    def should_close_trade(self, df, trade):
        current_price = df['close'].iloc[-1]
        current_trade=trade
        # Stop loss
        if current_trade["type"] == "buy" and current_price <= current_trade["stop_loss"]:
            return True
        
        if current_trade["type"] == "sell" and current_price >= current_trade["stop_loss"]:
            return True
        
        # Take profit
        if current_trade["type"] == "buy" and current_price >= current_trade["take_profit"]:
            return True
        
        if current_trade["type"] == "sell" and current_price <= current_trade["take_profit"]:
            return True

        # Time-based exit if trade is old
        if current_trade["duration"] > 4:  # 4 hours
            return True

        return False
