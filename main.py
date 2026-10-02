
from config.settings import *
from src.indicators.ema import EMAIndicator
from src.indicators.rsi import RSIIndicator
from src.indicators.macd import MACDIndicator
from src.indicators.fractals import FractalsIndicator
from src.indicators.atr import ATRIndicator
from src.strategies.strategy.entry import EntryLogic

from src.strategies.strategy.exit import ExitLogic
from src.strategies.strategy.filters import StrategyFilters
from src.strategies.strategy.rules import StrategyRules
from src.risk.risk_manager import RiskManager
from src.risk.trade_limit import TradeLimits
import pandas as pd
from src.backtesting.backtest_engine import BacktestEngine
from src.backtesting.metrics import PerformanceMetrics
from src.data_pipeline.clean_data import DataCleaner
from src.data_pipeline.validate_data import ValidateData
from src.feature_engineering.features import FeatureEngineer
from src.backtesting.portfolio import Portfolio
import os
from  src. analytics.performance import PerformanceAnalytics
#import data.run_pipeline as pipeline
def __init__(self):
       

        self.filters=StrategyFilters()

        # Indicators
        self.ema = EMAIndicator()
        self.rsi = RSIIndicator()
        self.macd = MACDIndicator()
        self.fractals = FractalsIndicator()
        self.atr = ATRIndicator()

       
     

        
        

def run(symbol="USDJPY"):
    processed_dir = os.path.join("data","processed")
    output_path = os.path.join(processed_dir,f"{symbol}_rade.csv")
    raw_dir = os.path.join("data","raw")
    raw_path = os.path.join(raw_dir,f"{symbol}M30.csv")
    print("📊 OFFLINE MODE (Backtesting & Optimization phase)")
    print(symbol)
    raw_df=pd.read_csv(raw_path,header=None, sep=None,engine="python",encoding="utf-16")
   
    clean_df=DataCleaner.clean(raw_df)

    print("Fetching data...")
     #ValidateData.validate(clean_df)

    print("Adding features...")
    feature_df=FeatureEngineer.add_features(clean_df)
    filters=StrategyFilters()
    rules=StrategyRules()
    # Create strategy instance
    entry_Logic = EntryLogic(rules,filters)
    exit_Logic = ExitLogic()
    
    trade_limits = TradeLimits()
    risk_manager = RiskManager(
            INITIAL_BALANCE,
            RISK_PER_TRADE, 
            MAX_LEVARAGE,
        )

    # Generate signals
    print("Running Backtesting Engine....")
    engine = BacktestEngine(entry_Logic, exit_Logic, risk_manager, trade_limits)
    trades = engine.run(feature_df)
    metrics=PerformanceMetrics(trades)
    print("\n========PERFORMANCE============")
    print("Metrics:", metrics.summary())
    
    
    portfolio=Portfolio(INITIAL_BALANCE)
    print("Trade history",len(portfolio.trade_history))
    print("Equity",len(portfolio.equity_curve))
    equity_curve=portfolio.equity_curve
    print(len(equity_curve))
   # PerformanceAnalytics.plot_equity_curve(equity_curve)
    
    
    for trade in trades.to_dict("records"):
        portfolio.execute_trade(trade)
    
        
    #print("Metrics:", portfolio.summary())
    
    trades=trades.to_csv(output_path,index=False)
    return trades

if __name__=="__main__":
    run()