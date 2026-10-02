import pandas as pd
#import logger as lg
class BacktestEngine:
    def __init__(self, entry_logic, exit_logic, risk_manager, trade_limits):
        self.entry_logic = entry_logic
        self.exit_logic = exit_logic
        self.risk_manager = risk_manager
        self.trade_limits = trade_limits
        self.trades = []

    def run(self, df):
        active_trade = None

        for i in range(200, len(df) - 1):
            window = df.iloc[:i]

           #ml_prob = predictor.predict(window)
            spread = 15  # fixed model spread

            # If trade is open → check exit
            if active_trade:
                active_trade['duration'] += 1

                if self.exit_logic.should_close_trade(window, active_trade):
                    active_trade['exit_price'] = window['close'].iloc[-1]
                    if active_trade["type"]=="sell":
                        
                       # strategy_logger.info(f"Cheking exit")
                        active_trade['exit_time']=window['datetime'].iloc[-1],
                        active_trade['profit'] = (
                        active_trade['entry_price'] - active_trade['exit_price']) * 100000*active_trade['lot_size']/active_trade['exit_price']
                    elif active_trade["type"]=="buy":
                        active_trade['exit_time']=window['datetime'].iloc[-1],
                        active_trade['profit'] = (
                        active_trade['exit_price'] - active_trade['entry_price']) * 100000*active_trade['lot_size']/active_trade['exit_price']
                        
                    self.trades.append(active_trade)
                    active_trade = None
                continue

            # No trade open → check entries
            if self.entry_logic.check_buy(window, spread):
                entry_price= window['close'].iloc[-1]
                
                stop, tp = self.risk_manager.calculate_buy_levels(entry_price, stop_loss_pips=15, take_profit_pips=50, pip_size=0.0001)
                lot = self.risk_manager.position_size(
                    stop_loss_pips=15, pip_value=10
                )
                #lot=1
                active_trade = {    
                    "type": "buy",
                    "entry_time":window['datetime'].iloc[-1],
                    
                    "entry_price": window['close'].iloc[-1],
                    "stop_loss": stop,
                    "take_profit": tp,
                    "lot_size": lot,
                    "duration": 0,
                    "direction_mult": 1
                }
              #  strategy_logger.info(f"BUY signal | Price={entry_price}")
                

            elif self.entry_logic.check_sell(window,  spread):
                entry_price= window['close'].iloc[-1]
                stop, tp = self.risk_manager.calculate_sell_levels(entry_price, stop_loss_pips=15, take_profit_pips=50, pip_size=0.0001)
                lot = self.risk_manager.position_size(
                    stop_loss_pips=15, pip_value=10
                )
                #lot=1
                active_trade = {
                    "type": "sell",
                    "entry_time":window['datetime'].iloc[-1],
                    "entry_price": window['close'].iloc[-1],
                    "stop_loss": stop,
                    "take_profit": tp,
                    "lot_size": lot,
                    "duration": 0,
                    "direction_mult": -1
                }
               # strategy_logger.info(f"SELL signal | Price={entry_price}")

        return pd.DataFrame(self.trades)
