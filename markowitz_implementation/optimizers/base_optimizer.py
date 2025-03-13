from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import sqlite3


DB_PATH = "/home/gafur/Documents/Finance/portfolio_optimization_project/markowitz_implementation/database/portfolio.db"

class BasePortfolioOptimizer(ABC):

    """Abstract base class for all portfolio optimization techniques."""


    def __init__(self, stock_data:pd.DataFrame, num_of_stocks:int, portfolio_id:int, method_name: str):
        """Initialize optimizer with stock data"""

        self.stock_data = stock_data
        self.num_of_stocks = num_of_stocks 
        self.portfolio_id = portfolio_id  
        self.method_name = method_name #Store Optimization Method Name

        #Compute essential Statistics
        self.returns = self.calculate_returns()
        self.mean_returns = self.calculate_mean_returns()
        self.cov_matrix = self.calculate_covariance()


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

        return self.num_of_stocks
    
    def save_results_to_db(self, best_portfolio):
        """Save optimized portfolio results to the database."""

        optimized_weights = str(best_portfolio['Portfolio Weights'])  # Convert to string
        expected_return = float(best_portfolio['Returns'])
        risk_metric = float(best_portfolio['Volatility'])
        sharpe_ratio = float(best_portfolio['Sharpe Ratio'])

        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            
            cursor.execute(
                """
                INSERT INTO portfolio_results (portfolio_id, method_name, optimized_weights, expected_return, risk_metric, sharpe_ratio) 
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (self.portfolio_id, self.method_name, optimized_weights, expected_return, risk_metric, sharpe_ratio)
            )

            connection.commit()
            print(f"Results saved: {self.method_name} (Portfolio {self.portfolio_id}) - Sharpe Ratio: {sharpe_ratio}.")
        
        except sqlite3.Error as e:
            print(f"Database error: {e}")

        finally:
            connection.close()



    @abstractmethod
    def optimize(self):
        """Abstract method to be implemented by subclasses."""
        pass