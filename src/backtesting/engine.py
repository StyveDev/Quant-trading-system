from src.backtesting.portfolio import Portfolio
from src.execution.broker import Broker


class BacktestEngine:
    def __init__(
        self,
        df,
        initial_balance,
        spread,
        commission,
        spillage
    ):
        self.df=df
        self.portfolio=Portfolio(initial_balance)
        self.broker=Broker(spread,commission,spillage)
    
    def run(self):
        
        for i in range(len(self.df)):
            row= self.df.iloc[i]  
            signal=row["signal"]
            close_price=row["close"]
            if signal==1 and self.portfolio.position==0:
                self.portfolio.open_position(1,close_price,size=1)
                execution_price= self.broker.execute_buy(close_price)
                self.portfolio.close_position(execution_price) 
            elif signal==-1:   
              
               
              self.portfolio.open_position(-1,close_price,size=1)  
              execution_price= self.broker.execute_sell(close_price)
              self.portfolio.close_position(execution_price) 
            self.portfolio.update_equity()
        return self.portfolio      