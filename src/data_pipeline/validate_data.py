class ValidateData:
    @staticmethod
    def validate(df):
        required_columns=[
            "datetime",
            "open",
            "high",
            "low",
            "close"
        ]
        for col in required_columns:
            if col not in df.colunmns:
                raise ValueError(f"Missing colunm:{col}")
            print("Data validation passed")
            
            return True