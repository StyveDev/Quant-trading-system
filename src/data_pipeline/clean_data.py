class DataCleaner:
    @staticmethod
    def clean(df):
        df= df.copy()
        df.columns = [
        "datetime",  
        "open", 
        "high", 
        "low",
        "close", 
        "volume",
      
        "x"
    ]
    
  
   
    #standardize column names
        df.columns = df.columns.str.strip().str.lower()
        df= df.drop(columns=["x"])
        #df= df.drop_dupicates()
        df= df.dropna()
        df= df.sort_values(by="datetime")
        
        df.reset_index(drop=True,inplace=True)
        
        return df