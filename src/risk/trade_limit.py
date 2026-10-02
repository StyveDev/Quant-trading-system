import time

class TradeLimits:
    def __init__(self, max_daily_loss=0.05, max_trades=10, cooldown_minutes=10):
        self.starting_equity = None
        self.max_daily_loss = max_daily_loss
        self.max_trades = max_trades
        self.cooldown_minutes = cooldown_minutes

        self.current_trades = 0
        self.last_loss_time = None

    # ------------------------------------
    # 1. RECORD STARTING EQUITY
    # ------------------------------------
    def set_starting_equity(self, balance):
        if self.starting_equity is None:
            self.starting_equity = balance

    # ------------------------------------
    # 2. DAILY LOSS LIMIT CHECK
    # ------------------------------------
    def within_daily_loss_limit(self, current_balance):
        drawdown = (self.starting_equity - current_balance) / self.starting_equity

        return drawdown <= self.max_daily_loss

    # ------------------------------------
    # 3. LIMIT MAX TRADES
    # ------------------------------------
    def can_take_more_trades(self):
        return self.current_trades < self.max_trades

    def register_trade(self):
        self.current_trades += 1

    # ------------------------------------
    # 4. COOL-DOWN ENFORCEMENT
    # ------------------------------------
    def start_cooldown(self):
        self.last_loss_time = time.time()

    def cooldown_active(self):
        if self.last_loss_time is None:
            return False

        elapsed = (time.time() - self.last_loss_time) / 60  # convert to minutes
        return elapsed < self.cooldown_minutes