import numpy as np

class PerformanceMetrics:
    def __init__(self, trades_df):
        self.df = trades_df
        

    
    def total_return(self):
        return self.df["profit"].sum()

    def winrate(self):
        wins = (self.df["profit"] > 0).sum()
        return wins / len(self.df) * 100

    def max_drawdown(self):
        equity = self.df["profit"].cumsum()
        peak = equity.cummax()
        dd = equity - peak
        return dd.min()
    
    def expectancy(self):
        trades= self.df["profit"].astype(float)
        wins=[t for t in trades if t > 0]
        losses=[abs(t)for t in trades if t <0]
        win_rate=len(wins)/len(losses)
        loss_rate =1-win_rate
        avg_win=sum(wins)/len(wins)if wins else 0
        avg_loss=sum(losses) / len(losses)if losses else 0
        expectancy = (win_rate*avg_win)-(loss_rate*avg_loss)
        return expectancy
    def sharpe(self, rf=0.0):
        returns = self.df["profit"]
        if returns.std() == 0:
            return 0
        return (returns.mean() - rf) / returns.std()
    
    
   
        

    def summary(self):
        return {
            "Total Return": round(self.total_return(),2),
            "Winrate %": round(self.winrate(),2),
            "Max Drawdown":round( self.max_drawdown(),2),
            "Sharpe Ratio": round(self.sharpe(),2),
            "Trades Taken": len(self.df),
            "Expectancy":self.expectancy()
        }
