class RiskManager:
    def __init__(self, account_balance, risk_percent, max_leverage):
        self.balance = account_balance
        self.risk_percent = risk_percent
        self.max_leverage = max_leverage

    # ----------------------------
    # 1. POSITION SIZE
    # ----------------------------
    def position_size(self, stop_loss_pips, pip_value):
        """
        Returns the lot size based on:
        risk = balance * risk_percent
        position_size = risk / (stop_loss_pips * pip_value)
        """
        risk_amount = self.balance * self.risk_percent
        lot = risk_amount / (stop_loss_pips * pip_value)
        return round(lot, 2)

    # ----------------------------
    # 2. STOP LOSS + TAKE PROFIT CALCULATOR
    # ----------------------------
    def calculate_buy_levels(self, entry_price, stop_loss_pips, take_profit_pips, pip_size=0.001):
        sl = entry_price - stop_loss_pips * pip_size
        tp = entry_price + take_profit_pips * pip_size
        return sl, tp
    def calculate_sell_levels(self,entry_price, stop_loss_pips, take_profit_pips, pip_size=0.001):
        sl = entry_price + stop_loss_pips * pip_size
        tp = entry_price - take_profit_pips * pip_size
        return sl, tp
    # ----------------------------
    # 3. ACCOUNT RISK EXPOSURE
    # ----------------------------
    def max_exposure(self, open_positions):
        """
        open_positions: list of lot sizes
        """
        total_lots = sum(open_positions)
        max_allowed = self.balance * 0.02  # 2% exposure rule
        return total_lots <= max_allowed

    # ----------------------------
    # 4. UPDATE BALANCE AFTER TRADE
    # ----------------------------
    def update_balance(self, profit_loss):
        self.balance += profit_loss
        return self.balance