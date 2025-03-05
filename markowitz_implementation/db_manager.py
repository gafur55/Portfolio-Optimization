import sqlite3
import os
from datetime import datetime
import pytz
import re


class DBManager():

    """This class handles the database for clients,
    storing name, selected stocks, and optimized weights
    of the stocks."""


    def __init__(self, db_folder="database", db_name="portfolio.db"):
        self.db_folder = db_folder
        self.db_path = os.path.join(self.db_folder, db_name)
        os.makedirs(self.db_folder, exist_ok=True)
        self._create_tables()


    def get_db_path(self):
        """Returns the database file path."""
        return self.db_path
    

    def _create_tables(self):
        """Creates tables for storing clients, portfolios, and portfolio results."""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executescript('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_name TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    symbols TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS portfolio_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_id INTEGER,
                    optimized_weights TEXT NOT NULL,
                    expected_return REAL,
                    risk_metric REAL,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE
                );
            ''')
            conn.commit()


    def add_client(self, client_name: str) -> int:
        """Adds a client if not already in the database and returns client ID."""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM clients WHERE client_name = ?", (client_name,))
            result = cursor.fetchone()

            if result:
                return result[0], True  # Client already exists, return ID

            cursor.execute("INSERT INTO clients (client_name) VALUES (?)", (client_name,))
            conn.commit()
            return cursor.lastrowid  # Return new client ID
        

    def add_portfolio(self, client_id: int, symbols: list[str]) -> int:
        """Adds a new stock portfolio for a client and returns portfolio ID."""   

        symbols_str = ",".join(symbols)
        # Get California time
        pacific = pytz.timezone("America/Los_Angeles")
        current_time = datetime.now(pacific)
        timezone_abbr = current_time.strftime("%Z")  # Gets PST or PDT
        # Format timestamp with timezone abbreviation
        current_time_pacific = current_time.strftime(f"%Y-%m-%d %H:%M:%S ({timezone_abbr})")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO portfolios (client_id, symbols, created_at) VALUES (?, ?, ?)", 
                (client_id, symbols_str, current_time_pacific)
            )
            conn.commit()
            return cursor.lastrowid  # Return portfolio ID


    def save_portfolio_results(self, portfolio_id: int, optimized_weights: dict, expected_return: float, risk_metric: float):
        """Saves portfolio optimization results for a specific portfolio."""

        weights_str = str(optimized_weights)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO portfolio_results (portfolio_id, optimized_weights, expected_return, risk_metric) VALUES (?, ?, ?, ?)",
                (portfolio_id, weights_str, expected_return, risk_metric)
            )
            conn.commit()


    def get_client_portfolios(self, client_id: int):
        """Fetches all portfolios for a given client."""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, symbols, created_at FROM portfolios WHERE client_id = ? ORDER BY created_at DESC", 
                (client_id,)
            )
            results = cursor.fetchall()
            return [{"portfolio_id": row[0], "symbols": row[1].split(","), "created_at": row[2]} for row in results] if results else None


    def get_portfolio_results(self, portfolio_id: int):
        """Retrieves portfolio optimization results for a given portfolio."""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT optimized_weights, expected_return, risk_metric FROM portfolio_results WHERE portfolio_id = ?",
                (portfolio_id,)
            )
            results = cursor.fetchall()
            return [{"allocation": eval(row[0]), "expected_return": row[1], "risk_metric": row[2]} for row in results] if results else None


    def get_client_id(self, client_name: str) -> int | None:
        """Fetches the client ID based on client name."""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM clients WHERE client_name = ?", (client_name,))
            result = cursor.fetchone()
            return result[0] if result else None  # Return client ID if found


    def delete_client(self, client_id: int):
        """Deletes a client and all their associated portfolios and results."""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            conn.commit()


    def get_all_clients(self):
        """Retrieves all clients from the database."""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, client_name FROM clients")
            clients = cursor.fetchall()
            return [{"id": row[0], "client_name": row[1]} for row in clients] if clients else None
        

    def display_all_clients(self):
        """Displays all clients in the database."""

        clients = self.get_all_clients()
        if not clients:
            print("No projects found in the database.\n")
            return
        
        print("\n📋 List of All Clients:")
        print("=" * 30)
        for client in clients:
            print(f"ID: {client['id']} | Name: {client['client_name']}")
        print("=" * 30)

 
    def client_exists(self, client_name: str) -> bool:
        """Checks if a client exists in the database."""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM clients WHERE client_name = ?", (client_name,))
            return cursor.fetchone() is not None  # Returns True if client exists, False otherwise


    def get_number_of_symbols(self, portfolio_id:int) -> int:
        """This function returns number of the stocks in the given portfolio"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT symbols FROM portfolios WHERE id = ?", (portfolio_id,))
            symbols = cursor.fetchone()
            symbols_str = symbols[0]
            symbols_list = re.split(r"\W+", symbols_str)
            return(len(symbols_list))
        
