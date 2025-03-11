from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import db_manager 



class BasePortfolioOptimizer(ABC):

    """Abstract base class for all portfolio optimization techniques."""


    def __init__(self, stock_data:pd.DataFrame, db_manager:db_manager, portfolio_id:int):
        """Initialize optimizer with stock data and database manager"""

        self.stock_data = stock_data
        self.db_manager = db_manager  
        self.portfolio_id = portfolio_id  
        self.returns = self.calculate_returns()
        self.mean_returns = self.calculate_mean_returns()
        self.cov_matrix = self.calculate_covariance()
        self.num_assets = self.get_num_assets()  

    def calculate_returns(self):
        """Compute daily returns."""

        return self.stock_data.pct_change()
    
    def calculate_mean_returns(self):
        """Compute mean returns."""

        return self.returns.mean()
    
    def calculate_covariance(self):
        """Compute covariance matrix."""

        return self.returns.cov()
    
    def get_num_assets(self):
        """Fetch number of stocks in the portfolio from database."""

        return self.db_manager.get_number_of_symbols(self.portfolio_id)
    
    @abstractmethod
    def optimize(self):
        """Abstract method to be implemented by subclasses."""
        pass