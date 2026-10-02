class Portfolio:
    def __init__(self,initial_balance):
        self.initial_balance=initial_balance
        self.balance=initial_balance
        self.equity=initial_balance
        
        self.total_profit=0
        self.wins=0
        self.losses=0
        self.total_trades=0
        self.trade_history=[]
        self.equity_curve = [self.equity]
        
    def execute_trade(self,trade):
       
        
        #trade_type=trade['direction']
        entry_price=trade["entry_price"]
        exit_price=trade["exit_price"]
        tp_price=trade.get("take_profit")
        sl_price=trade.get("stop_loss")
        duratoin=trade.get("duratoin")
        profit=trade.get("profit")
        #update balance
        self.balance+=profit
        self.equity+=self.balance
        
        #update statistics
        self.total_profit+=profit
        self.total_trades+=1
        
        if profit>0:
            self.wins+=1
        else:
            self.losses+=1 
            
        #save trades
        self.trade_history.append({
            
            "entry":entry_price,
            "exit":exit_price,
            "tp":tp_price,
            "sl":sl_price,
            "duratoin":duratoin,
            "profit":profit,
            "balance":self.balance
        })  
            
        self.equity_curve.append(self.balance)
    def summary(self):
        win =0
        if self.total_trades>0:
            win_rate=(self.wins/self.total_trades)*100
        return{
            "Final Balance:":self.balance,
            "Total Profit:":self.total_profit,
            "Total Trades:":self.total_trades,
            "Win:":self.wins,
            "Losses:":self.losses,
            "Win Rate:":win_rate
            #"Equty curve":self.equity_curve
            
        }    
            