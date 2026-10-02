import matplotlib.pyplot as plt
import numpy as np
class PerformanceAnalytics:
    def plot_equity_curve(equity_curve):
        equity=np.array(equity_curve)
        running_max= np.maximum.accumulate(equity)
        drawdown=(running_max-equity)/running_max
        plt.figure(figsize=(12,6))
        plt.plot(equity,label="Equity")
        plt.fill_between(
            range(len(drawdown)),
            equity,
            running_max,
            alpha=0.3,
            label="Drawdown"
            
        )
        plt.legend()
       
        plt.grid()
        plt.show()
        