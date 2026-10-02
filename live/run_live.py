import pandas as pd
import MetaTrader5 as mt5
from time import sleep

class LiveRunner:
    def __init__(self, connection, order_manager, entry_logic, exit_logic, position_sizer, trade_limits, predictor):
        self.connection = connection
        self.order_manager = order_manager
        self.entry_logic = entry_logic
        self.exit_logic = exit_logic
        self.position_sizer = position_sizer
        self.trade_limits = trade_limits
        self.predictor = predictor
        self.active_trade = None

    def run(self, symbol, timeframe, bars=500):
        print("[LIVE] Starting live trading loop...")

        while True:
            rates = self.connection.get_data(symbol, timeframe, bars)
            df = pd.DataFrame(rates)

            spread = self.order_manager.get_spread()
            ml_prob = self.predictor.predict(df)

            # EXIT CHECK
            if self.active_trade:
                if self.exit_logic.should_close_trade(df, self.active_trade):
                    print("[LIVE] Closing trade...")
                    mt5.Close(self.active_trade["type"])
                    self.active_trade = None
                sleep(1)
                continue

            # ENTRY CHECK — BUY
            if self.entry_logic.check_buy(df, ml_prob, spread):
                sl, tp = self.trade_limits.compute_sl_tp(df, "buy")
                lot = self.position_sizer.calc_lot_size(stop_loss_pips=20)

                result = self.order_manager.send_buy(lot, sl, tp)
                print("[LIVE] BUY EXECUTED →", result)

                self.active_trade = {
                    "type": "buy",
                    "stop_loss": sl,
                    "take_profit": tp
                }

            # ENTRY CHECK — SELL
            elif self.entry_logic.check_sell(df, ml_prob, spread):
                sl, tp = self.trade_limits.compute_sl_tp(df, "sell")
                lot = self.position_sizer.calc_lot_size(stop_loss_pips=20)

                result = self.order_manager.send_sell(lot, sl, tp)
                print("[LIVE] SELL EXECUTED →", result)

                self.active_trade = {
                    "type": "sell",
                    "stop_loss": sl,
                    "take_profit": tp
                }

            sleep(1)
