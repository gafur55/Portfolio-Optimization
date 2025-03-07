import yfinance as yf
import pandas as pd

class DataFetcher:
    def __init__(self, stock_symbols:list[str], should_download:bool, start_date:str = "2022-01-01", end_date:str = "2025-01-01"):
        """Initialize the DataFetcher."""
        
        self.stock_symbols = stock_symbols
        self.start_date = start_date
        self.end_date = end_date
        self.should_download = should_download

    def fetch_stock_data(self):
        """Fetch historical stock prices from Yahoo Finance."""

        stock_data = {}
        for symbol in self.stock_symbols:
            stock = yf.download(symbol, start=self.start_date, end=self.end_date)
            print(stock)
            if not stock.empty:
                stock_data[symbol] = stock["Close"]     
        return pd.DataFrame(stock_data)

    def preprocess_data(self, stock_data: pd.DataFrame):
        """Preprocess stock data for portfolio optimization."""
        # Calculate daily returns

    def download_data_locally(self, stock_symbols:list[str], start_date: str = "2022-01-01", end_date: str = "2025-01-01"):
        """Downloads the data locally"""



test = DataFetcher(['NVDA', 'AAPL', 'TSLA'], False)
data = test.fetch_stock_data()
print(data)
