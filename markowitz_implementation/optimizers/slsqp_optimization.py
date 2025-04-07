from base_optimizer import BasePortfolioOptimizer
import numpy as np
import pandas as pd
import scipy.optimize as sci_opt



class SLSQPOptimizer(BasePortfolioOptimizer):
    """Sequential Least Squares Programming (SLSQP) Optimizer."""

    def __init__(self, stock_data, num_of_stocks, portfolio_id):
        super().__init__(stock_data, num_of_stocks, portfolio_id, method_name="SLSQP")
        self._log_return = np.log(1 + self.calculate_returns())
        self._optimized_result = self.optimize()
        self._optimized_metrics = self.get_optimized_metrics()
        self.save_results_to_db(self.get_optimized_metrics())


    def get_metrics(self, weights: list) -> np.array:
        """
        With a given set of weights, return the portfolio returns,
        the portfolio volatility, and the portfolio sharpe ratio.
        """
        self.weights = np.array(weights)

        ret = np.sum(self._log_return.mean() * weights) * 252

        vol = np.sqrt(
            np.dot(weights.T, np.dot(self._log_return.cov() * 252, weights))
        )

        sr = ret / vol

        return np.array([ret, vol, sr])


    def grab_negative_sharpe(self, weights: list) -> np.array:
        """The function to minimize (negative Sharpe Ratio)."""
        return -self.get_metrics(weights)[2]


    def check_sum(self, weights: list) -> float:
        """Ensure the allocations of the weights sum to 1 (100%)."""
        return np.sum(weights) - 1


    def optimize(self):
        """Run SLSQP optimization to maximize Sharpe Ratio."""
        bounds = tuple((0, 1) for _ in range(self.num_of_stocks))

        constraints = {'type': 'eq', 'fun': self.check_sum}

        init_guess = self.num_of_stocks * [1 / self.num_of_stocks]

        optimized_result = sci_opt.minimize(
            self.grab_negative_sharpe,
            init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return optimized_result


    def get_optimized_metrics(self):
        """Get the metrics (Return, Volatility, Sharpe Ratio) of optimized portfolio."""
        if self._optimized_result.success:
            optimized_weights = self._optimized_result.x
            metrics = self.get_metrics(weights=optimized_weights)

            return {
                'Returns': metrics[0],
                'Volatility': metrics[1],
                'Sharpe Ratio': metrics[2],
                'Portfolio Weights': optimized_weights
            }
        else:
            raise ValueError("Optimization failed! Reason: " + self._optimized_result.message)


    def get_result(self):
        """Get the raw optimizer result object (scipy OptimizeResult)."""
        return self._optimized_result








# symbols = ['AAPL', 'GOOGL', 'MSFT']
# data_fetcher = DataFetcher(symbols, False)
# stock_data = data_fetcher.fetch_stock_data()

# num_of_stocks = len(symbols)

# slsqp_optimizer = SLSQPOptimizer(stock_data, num_of_stocks, portfolio_id=5)

# # To get optimized portfolio info
# result = slsqp_optimizer.get_optimized_metrics()

# print('Optimized Return:', result['Returns'])
# print('Optimized Volatility:', result['Volatility'])
# print('Optimized Sharpe Ratio:', result['Sharpe Ratio'])
# print('Optimized Portfolio Weights:', result['Portfolio Weights'])
