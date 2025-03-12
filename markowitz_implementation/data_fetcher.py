import yfinance as yf
import pandas as pd
import os
from datetime import datetime


class DataFetcher:
    def __init__(self, stock_symbols:list[str], should_download:bool, start_date:str = "2020-01-01", end_date:str = "2025-01-01"):
        """Initialize the DataFetcher."""
        
        self.stock_symbols = stock_symbols
        self.start_date = start_date
        self.end_date = end_date
        self.should_download = should_download


    def fetch_stock_data(self):
        """Fetch historical Close prices from Yahoo Finance.
        Only consists of Ticker Symbol, Date and Close Price"""

        data = yf.download(self.stock_symbols, start=self.start_date, end=self.end_date)["Close"]
        if self.should_download:
            self.download_data_locally(data)

        return data


    def download_data_locally(self, data: pd.DataFrame):
        """Downloads the data locally if needed"""

        current_dir = os.getcwd()
        stock_data_dir = os.path.join(current_dir, "stock_data")
        os.makedirs(stock_data_dir, exist_ok=True)
        symbols_str = "_".join(self.stock_symbols)[:50]     #truncate if the name is too long
        filename = f"stocks_{symbols_str}_{datetime.now().strftime('%Y-%m-%d')}.csv"
        file_path = os.path.join(stock_data_dir, filename)
        data.to_csv(file_path) 





# test = DataFetcher(['AAPL', 'TSLA'], False)
# data = test.fetch_stock_data()
# print(data)
