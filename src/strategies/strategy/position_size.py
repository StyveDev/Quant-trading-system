class PositionSizer:
    def __init__(self, balance, risk_percent):
        self.balance = balance
        self.risk_percent = risk_percent

    def calc_lot_size(self, stop_loss_pips, pip_value=10):
        risk_amount = self.balance * self.risk_percent
        lot_size = risk_amount / (stop_loss_pips * pip_value)
        return round(lot_size, 2)
