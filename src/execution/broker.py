class Broker:
    def __init__(self,spread,commission,spillage):
        self.spread=spread
        self.commission=commission
        self.spillage=spillage
        
    def execute_buy(self,price):
            return price+self.spread+self.spillage
        
    def execute_sell(self,price):
            return price-self.spread-self.spillage
        