import logging
import os

#create logs foder automatically
os.makedirs("logs",exit_ok=True)

def  setup_logger(name,log_file,level=logging.INFO):
    
    logger=logging.getLogger(name)
    #prevent duplicate logs
    if logger.hasHandlers():
        return logger
    logger.setLevel(level)
    
    formatter= logging.Formatter(
        "%(asctime)s|%(levelname)s|%(message)s"
    )
    
    file_handler= logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
#Individual loggers

strategy_logger=setup_logger("strategy_logger","logs/strategy.log")
execution_logger=setup_logger("execution_logger","logs/execution.log")
portfolio_logger=setup_logger("portfolio_logger","logs/portfolio.log")
risk_logger=setup_logger("risk_logger","logs/risk.log")
errors_logger=setup_logger("errors_logger","logs/errors.log")