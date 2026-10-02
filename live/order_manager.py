# live/order_manager.py

import MetaTrader5 as mt5
from logs.trade_logger import TradeLogger
from logs.error_logger import log_error
from strategy.position_size import calculate_position_size
from risk.risk_manager import RiskManager


class OrderManager:

    def __init__(self, magic=202501):
        self.magic = magic
        self.risk_manager = RiskManager()

    # ----------------------------------------
    # INITIALIZATION
    # ----------------------------------------
    def initialize(self):
        if not mt5.initialize():
            log_error("❌ MT5 failed to initialize")
            return False
        return True

    # ----------------------------------------
    # HELPER: FORMAT ORDER
    # ----------------------------------------
    def _build_request(self, action, symbol, volume, sl, tp):
        order_type = mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL

        return {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "sl": sl,
            "tp": tp,
            "magic": self.magic,
            "comment": f"quant_bot_{action.lower()}",
            "type_filling": mt5.ORDER_FILLING_FOK
        }

    # ----------------------------------------
    # GET CURRENT PRICE
    # ----------------------------------------
    def get_price(self, symbol, action):
        tick = mt5.symbol_info_tick(symbol)
        return tick.ask if action == "BUY" else tick.bid

    # ----------------------------------------
    # SEND BUY ORDER
    # ----------------------------------------
    def send_buy(self, symbol, stop_loss_pips, take_profit_pips):

        if not self.risk_manager.can_trade():
            log_error("RiskManager blocked BUY trade.")
            return None

        price = self.get_price(symbol, "BUY")
        volume = calculate_position_size(symbol, stop_loss_pips)

        sl = price - (stop_loss_pips * 0.0001)
        tp = price + (take_profit_pips * 0.0001)

        request = self._build_request("BUY", symbol, volume, sl, tp)
        result = mt5.order_send(request)

        if result.retcode == mt5.RES_OK:
            TradeLogger.log_trade(
                action="BUY",
                symbol=symbol,
                volume=volume,
                price=result.price,
                sl=sl,
                tp=tp,
                comment="BUY executed"
            )
            return result
        else:
            log_error("BUY failed", result)
            return None

    # ----------------------------------------
    # SEND SELL ORDER
    # ----------------------------------------
    def send_sell(self, symbol, stop_loss_pips, take_profit_pips):

        if not self.risk_manager.can_trade():
            log_error("RiskManager blocked SELL trade.")
            return None

        price = self.get_price(symbol, "SELL")
        volume = calculate_position_size(symbol, stop_loss_pips)

        sl = price + (stop_loss_pips * 0.0001)
        tp = price - (take_profit_pips * 0.0001)

        request = self._build_request("SELL", symbol, volume, sl, tp)
        result = mt5.order_send(request)

        if result.retcode == mt5.RES_OK:
            TradeLogger.log_trade(
                action="SELL",
                symbol=symbol,
                volume=volume,
                price=result.price,
                sl=sl,
                tp=tp,
                comment="SELL executed"
            )
            return result
        else:
            log_error("SELL failed", result)
            return None

    # ----------------------------------------
    # CLOSE ORDER
    # ----------------------------------------
    def close_position(self, ticket, symbol):

        position = mt5.positions_get(ticket=ticket)
        if not position:
            log_error(f"Position not found (ticket={ticket})")
            return None

        pos = position[0]
        action = "SELL" if pos.type == mt5.ORDER_TYPE_BUY else "BUY"
        price = self.get_price(symbol, action)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": pos.volume,
            "type": mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY,
            "position": ticket,
            "price": price,
            "magic": self.magic,
            "comment": "quant_bot_close"
        }

        result = mt5.order_send(request)

        if result.retcode == mt5.RES_OK:
            TradeLogger.log_trade(
                action="CLOSE",
                symbol=symbol,
                volume=pos.volume,
                price=result.price,
                sl=pos.sl,
                tp=pos.tp,
                comment=f"Closed order #{ticket}"
            )
            return result
        else:
            log_error(f"Close failed (ticket={ticket})", result)
            return None
