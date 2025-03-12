import pandas as pd
from monte_carlo_optimizer import MonteCarloOptimizer

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_manager import DBManager
from data_fetcher import DataFetcher

portfolio_id = 6
db_manager = DBManager()

# print(db_manager.get_portfolio_symbols(1))

data_fetcher = DataFetcher(db_manager.get_portfolio_symbols(portfolio_id), False)
tick_data = data_fetcher.fetch_stock_data()

num_of_stocks = db_manager.get_number_of_symbols(portfolio_id)

monte_carlo_optimizer = MonteCarloOptimizer(tick_data, num_of_stocks, portfolio_id)

# print(monte_carlo_optimizer)

print('')
print('='*80)
print('MAX SHARPE RATIO:')
print('-'*80)
print(monte_carlo_optimizer.get_max_sharpe_ratio())
print('-'*80)

print('')
print('='*80)
print('MIN VOLATILITY:')
print('-'*80)
print(monte_carlo_optimizer.get_min_volatility())
print('-'*80)