from db_manager import DBManager
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

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
        return

    table = Table(title=f"📊 [bold cyan]Portfolios of {client_name}[/bold cyan]", header_style="bold yellow")
    table.add_column("Portfolio ID", justify="center", style="bold green")
    table.add_column("Stocks", style="bold white")
    table.add_column("Created At", style="bold magenta")

    for p in portfolios:
        table.add_row(str(p["portfolio_id"]), ", ".join(p["symbols"]), p["created_at"])

    console.print(table)

def main():
    """Main function to interact with the user and manage portfolios."""
    db = DBManager()

    # Display all clients at the start
    display_clients(db)

    # Get client name with a visual input prompt
    client_name = Prompt.ask("[bold cyan]Enter client name[/bold cyan]").strip()

    # Check if client exists
    if db.client_exists(client_name):
        console.print(f"✅ [bold green]Client '{client_name}' found in the database![/bold green]")
        client_id = db.get_client_id(client_name)

        # Ask whether to display portfolios or add a new one
        while True:
            action = Prompt.ask("[bold yellow]Do you want to (1) Display portfolios or (2) Add a new portfolio?[/bold yellow]", choices=["1", "2"])

            if action == "1":
                display_portfolios(db, client_id, client_name)
                break  # Exit loop after displaying portfolios
            
            elif action == "2":
                # Get stock symbols with a visually formatted input
                symbols_input = Prompt.ask(f"[bold cyan]Enter stock symbols for {client_name} (comma-separated)[/bold cyan]").strip()
                symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

                if not symbols:
                    console.print("[bold red]⚠️ No valid symbols entered. Portfolio was not created.[/bold red]")
                else:
                    # Add portfolio
                    portfolio_id = db.add_portfolio(client_id, symbols)
                    console.print(f"✅ [bold green]Portfolio created! ID: {portfolio_id}, Stocks: {', '.join(symbols)}[/bold green]")
                break  # Exit loop after adding portfolio

    else:
        console.print(f"⚠️ [bold yellow]Client '{client_name}' not found. Creating a new client...[/bold yellow]")
        client_id = db.add_client(client_name)

        # Get stock symbols with a visually formatted input
        symbols_input = Prompt.ask(f"[bold cyan]Enter stock symbols for {client_name} (comma-separated)[/bold cyan]").strip()
        symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

        if not symbols:
            console.print("[bold red]⚠️ No valid symbols entered. Portfolio was not created.[/bold red]")
            return

        # Add portfolio
        portfolio_id = db.add_portfolio(client_id, symbols)
        console.print(f"✅ [bold green]Portfolio created! ID: {portfolio_id}, Stocks: {', '.join(symbols)}[/bold green]")

if __name__ == "__main__":
    main()
