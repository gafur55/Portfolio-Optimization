import sqlite3
import os


class DBManager():

    """This class handles the database for clients,
    storing name, selected stocks, and optimized weights
    of the stocks."""


    def __init__(self, db_folder = "database", db_name = "portfolio.db"):
        self.db_folder = db_folder
        self.db_path = os.path.join(self.db_folder, db_name)
        os.makedirs(self.db_folder, exist_ok=True)
        self._create_tables()

    def get_db_path(self):
        """Returns the database file path."""
        return self.db_path
    
    def _create_tables(self):
        """Creates tables for storing client data 
        and portfolio optimization results."""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            #fixme??? Sharpe ratio metric might be needed in portfolio results table
            cursor.executescript('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_name TEXT NOT NULL,
                    symbols TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS portfolio_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    optimized_weights TEXT NOT NULL,
                    expected_return REAL,
                    risk_metric REAL,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
                );        
            ''')
            conn.commit()

    def add_client(self, client_name:str, symbols:list[str]) -> int:
        """Adds a new client with their selected stocks and
         returns the assigned client ID."""

        symbols_str = ",".join(symbols)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clients (client_name, symbols) VALUES (?, ?)", (client_name, symbols_str))
            conn.commit()
            return cursor.lastrowid
        
    def get_client_data(self, client_id:int):
        """Fetches selected stocks for a given client"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT client_name, symbols FROM clients WHERE id = ?", (client_id),) #comma makes client_id a tuple
            result = cursor.fetchone()
            if result:
                return {"client_name": result[0], "symbols": result[1].split(",")}
            return None #client not found

    def save_portfolio_results(self, client_id:int, optimized_weights:dict, expected_return:float, risk_metric:float):
        """Saves portfolio optimization results for the client"""    

        weights_str = str(optimized_weights)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO portfolio_results (client_id, optimized_weights, expected_return, risk_metric) VALUES (?, ?, ?, ?)",
                (client_id, weights_str, expected_return, risk_metric)
            )
            conn.commit()

    def get_portfolio_results(self, client_id:int):
        """Retrieves all portfolio optimization results for a given client."""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT optimized_weights, expected_return, risk_metric FROM portfolio_results WHERE client_id = ?", (client_id,))
            results = cursor.fetchall()
            return [{"allocation": eval(row[0]), "expected_return": row[1], "risk_metric": row[2]} for row in results] if results else None

    def get_all_clients(self):
        """Retrieves all clients from the database."""

    def get_all_portfolio_results(self):
        """Retrieves all stored portfolio optimization results."""

    def delete_client(self, client_id: int):
        """Deletes a client and all their associated portfolio 
        results (due to ON DELETE CASCADE)."""
        




testdb = DBManager()
