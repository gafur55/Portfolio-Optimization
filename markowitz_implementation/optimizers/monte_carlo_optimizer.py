import numpy as np
import pandas as pd
from base_optimizer import BasePortfolioOptimizer


class MonteCarloOptimizer(BasePortfolioOptimizer):

    """Monte Carlo Simulation"""


    def __init__(self, stock_data, num_of_stocks, portfolio_id):
        super().__init__(stock_data, num_of_stocks, portfolio_id, method_name="Monte Carlo Simulation")
        self._simulations_df = self.optimize()
        self._max_sharpe_ratio = self.set_max_sharpe_ratio()
        self._min_volatility = self.set_min_volatility()
        self.save_results_to_db(self.get_max_sharpe_ratio())


    def optimize(self, num_simulations=10000):
        # Calculate the log of returns
        log_return = np.log(1 + self.calculate_returns())

        #Prep an array to store the weights as they are generated, 10000 iterations for each of our 4 symbols.
        all_weights = np.zeros((num_simulations, self.get_num_assets()))

        # Prep an array to store the returns as they are generated, 10000 possible return values.
        ret_arr = np.zeros(num_simulations)

        # Prep an array to store the volatilities as they are generated, 10000 possible volatility values.
        vol_arr = np.zeros(num_simulations)

        # Prep an array to store the sharpe ratios as they are generated, 10000 possible Sharpe Ratios.
        sharpe_arr = np.zeros(num_simulations)

        #Simulation starts.
        for ind in range(num_simulations):

            # First, calculate the weights.
            weights = np.array(np.random.random(self.get_num_assets())) #Randomly chosen weights
            weights = weights / np.sum(weights)

            # Add the weights, to the `weights_arrays`.
            all_weights[ind, :] = weights

            # Calculate the expected log returns, and add them to the `returns_array`.
            ret_arr[ind] = np.sum((log_return.mean() * weights) * 252)
            
            # Calculate the volatility (SD of the portfolio), and add them to the `volatility_array`.
            vol_arr[ind] = np.sqrt(
                np.dot(weights.T, np.dot(log_return.cov() * 252, weights))
            )

            # Calculate the Sharpe Ratio and Add it to the `sharpe_ratio_array`.
            sharpe_arr[ind] = ret_arr[ind]/vol_arr[ind]
        
        # Combine all Return, Volatility, Sharpe Ratio, Weights data into single dataframe
        simulations_data = [ret_arr, vol_arr, sharpe_arr, all_weights]

        simulations_df = pd.DataFrame(data=simulations_data).T

        simulations_df.columns = [
            'Returns',
            'Volatility',
            'Sharpe Ratio',
            'Portfolio Weights'
        ]

        simulations_df = simulations_df.infer_objects()
        
        return simulations_df
    

    def set_max_sharpe_ratio(self):
        """Set the Max Sharpe Ratio from the run."""

        return self._simulations_df.loc[self._simulations_df['Sharpe Ratio'].idxmax()]

    
    def get_max_sharpe_ratio(self):
        """Get the Max Sharpe Ratio from the run."""

        return self._max_sharpe_ratio
    

    def set_min_volatility(self):
        """Set the Min Volatility from the run."""

        return self._simulations_df.loc[self._simulations_df['Volatility'].idxmin()]
        

    def get_min_volatility(self):
        """Get the Min Volatility from the run."""

        return self._min_volatility