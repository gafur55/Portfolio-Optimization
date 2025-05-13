import sys
import os

# Get the absolute path of the "optimizers" directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "optimizers")))

from db_manager import DBManager
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from optimizers.monte_carlo_optimizer import MonteCarloOptimizer  # ✅ Fix Import

from data_fetcher import DataFetcher

from optimizers.slsqp_optimization import SLSQPOptimizer

# Initialize Rich Console
console = Console()




def display_clients(db):
    """Displays all existing clients in a visually appealing format."""

    clients = db.get_all_clients()
    
    if not clients:
        console.print("[bold red]⚠️ No clients found in the database.[/bold red]")
        return
    
    table = Table(title="📋 [bold cyan]Existing Clients[/bold cyan]", header_style="bold yellow")
    table.add_column("Client ID", justify="center", style="bold green")
    table.add_column("Name", style="bold white")

    for client in clients:
        table.add_row(str(client["id"]), client["client_name"])

    console.print(table)



def display_portfolios(db, client_id, client_name):
    """Displays all portfolios for a given client in a formatted table."""

    portfolios = db.get_client_portfolios(client_id)

    if not portfolios:
        console.print(f"[bold yellow]⚠️ No portfolios found for [cyan]{client_name}[/cyan].[/bold yellow]")
        return None

    table = Table(title=f"📊 [bold cyan]Portfolios of {client_name}[/bold cyan]", header_style="bold yellow")
    table.add_column("Portfolio ID", justify="center", style="bold green")
    table.add_column("Stocks", style="bold white")
    table.add_column("Created At", style="bold magenta")

    for p in portfolios:
        table.add_row(str(p["portfolio_id"]), ", ".join(p["symbols"]), p["created_at"])

    console.print(table)

    return portfolios  # Return portfolio list for further processing



def optimize_portfolio(db, portfolio_id, symbols):
    """Runs portfolio optimization (Monte Carlo and SLSQP) and saves the results to the database."""

    # Fetch stock data
    data_fetcher = DataFetcher(symbols, True)  # False means no caching
    stock_data = data_fetcher.fetch_stock_data()

    # Get number of stocks
    num_of_stocks = len(symbols)

    # 1. Run Monte Carlo
    console.print(f"\n⚡ [bold cyan]Running Monte Carlo Optimization for Portfolio {portfolio_id}...[/bold cyan]\n")
    monte_carlo_optimizer = MonteCarloOptimizer(stock_data, num_of_stocks, portfolio_id)

    # 2. Run SLSQP
    console.print(f"\n⚡ [bold cyan]Running SLSQP Optimization for Portfolio {portfolio_id}...[/bold cyan]\n")
    slsqp_optimizer = SLSQPOptimizer(stock_data, num_of_stocks, portfolio_id)

    # Both optimizations save results automatically
    # Show optimization results
    display_optimization_results(db, portfolio_id)



def display_optimization_results(db, portfolio_id):
    """Fetch and display previous optimization results for a portfolio."""

    results = db.get_portfolio_results(portfolio_id)

    if not results:
        console.print("[bold red]❌ No optimization results found for this portfolio.[/bold red]")
        return

    # Fetch stock symbols separately
    stock_symbols = db.get_portfolio_symbols(portfolio_id)

    table = Table(title=f"📊 [bold cyan]Optimization Results for Portfolio {portfolio_id}[/bold cyan]", header_style="bold yellow")
    table.add_column("Method", style="bold white")
    table.add_column("Expected Return", justify="center", style="bold green")
    table.add_column("Volatility (Risk)", justify="center", style="bold red")
    table.add_column("Sharpe Ratio", justify="center", style="bold magenta")
    table.add_column("Stock Allocations", style="bold blue")  # ✅ Added new column

    for i, result in enumerate(results):
        weight_values = result["allocation"]  # NumPy array or list
        if len(weight_values) != len(stock_symbols):
            console.print("[bold red]⚠️ Mismatch between stock symbols and weights![/bold red]")
            continue

        # Match stock symbols with weights, showing 4 decimal places
        formatted_allocations = "\n".join([f"{symbol}: {weight:.4%}" for symbol, weight in zip(stock_symbols, weight_values)])

        # ✅ Insert a separator after each portfolio result
        if i > 0:
            table.add_row("─" * 20, "─" * 15, "─" * 17, "─" * 12, "─" * 20, end_section=True)

        method_name = result.get("method_name", "Unknown Method")  # Pull the method name

        table.add_row(
            method_name,
            f"{result['expected_return']:.4%}",
            f"{result['risk_metric']:.4%}",
            f"{result['sharpe_ratio']:.4f}",
            formatted_allocations
        )

    console.print(table)



def main():
    """Main function to run the portfolio optimization program."""
    db = DBManager()

    # Display all clients at the start
    display_clients(db)

    # Get client name
    client_name = Prompt.ask("[bold cyan]Enter client name[/bold cyan]").strip()
    
    # Check if user wants to exit
    if client_name.lower() == 'q':
        console.print("[bold yellow]Goodbye![/bold yellow]")
        return

    # Check if client exists
    client_id = db.get_client_id(client_name)

    if client_id:
        console.print(f"✅ [bold green]Client '{client_name}' found![/bold green]")

        # Ask whether to display portfolios, add a new one, or optimize
        while True:
            action = Prompt.ask("[bold yellow]Do you want to (1) Display portfolios, (2) Add a new portfolio, (3) Optimize a portfolio, or (q) Quit?[/bold yellow]", choices=["1", "2", "3", "q"])

            if action.lower() == "q":
                console.print("[bold yellow]Goodbye![/bold yellow]")
                return

            if action == "1":
                portfolios = display_portfolios(db, client_id, client_name)
                if not portfolios:
                    continue

                portfolio_id = Prompt.ask("[bold cyan]Enter Portfolio ID to view optimization results or press Enter to skip[/bold cyan]", default="").strip()
                if portfolio_id.lower() == 'q':
                    console.print("[bold yellow]Goodbye![/bold yellow]")
                    return
                if portfolio_id:
                    display_optimization_results(db, int(portfolio_id))

            elif action == "2":
                # Get stock symbols
                symbols_input = Prompt.ask(f"[bold cyan]Enter stock symbols for {client_name} (comma-separated) or 'q' to quit[/bold cyan]").strip()
                if symbols_input.lower() == 'q':
                    console.print("[bold yellow]Goodbye![/bold yellow]")
                    return
                symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

                if not symbols:
                    console.print("[bold red]⚠️ No valid symbols entered. Portfolio was not created.[/bold red]")
                else:
                    portfolio_id = db.add_portfolio(client_id, symbols)
                    console.print(f"✅ [bold green]Portfolio created! ID: {portfolio_id}, Stocks: {', '.join(symbols)}[/bold green]")

            elif action == "3":
                portfolios = display_portfolios(db, client_id, client_name)
                if not portfolios:
                    continue

                portfolio_id = Prompt.ask("[bold cyan]Enter Portfolio ID to optimize or 'q' to quit[/bold cyan]")
                if portfolio_id.lower() == 'q':
                    console.print("[bold yellow]Goodbye![/bold yellow]")
                    return
                portfolio_id = int(portfolio_id)
                portfolio_symbols = db.get_portfolio_symbols(portfolio_id)

                optimize_portfolio(db, portfolio_id, portfolio_symbols)

    else:
        console.print(f"⚠️ [bold yellow]Client '{client_name}' not found. Creating a new client...[/bold yellow]")
        client_id = db.add_client(client_name)

        # Get stock symbols
        symbols_input = Prompt.ask(f"[bold cyan]Enter stock symbols for {client_name} (comma-separated) or 'q' to quit[/bold cyan]").strip()
        if symbols_input.lower() == 'q':
            console.print("[bold yellow]Goodbye![/bold yellow]")
            return
        symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

        if not symbols:
            console.print("[bold red]⚠️ No valid symbols entered. Portfolio was not created.[/bold red]")
            return

        # Add portfolio
        portfolio_id = db.add_portfolio(client_id, symbols)
        console.print(f"✅ [bold green]Portfolio created! ID: {portfolio_id}, Stocks: {', '.join(symbols)}[/bold green]")

if __name__ == "__main__":
    main()
