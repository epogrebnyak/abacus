import typer
from typing_extensions import Annotated

from abacus.base import Amount

app = typer.Typer(
    add_completion=False, help="A minimal yet valid double entry accounting system."
)
chart = typer.Typer(help="Modify chart of accounts.", add_completion=False)
add = typer.Typer(help="Add accounts to chart.", add_completion=False)
app.add_typer(chart, name="chart")
chart.add_typer(add, name="add")


@app.command()
def about():
    """Show information about `abacus` package."""
    print("abacus")


@app.command()
def init(company_name: str):
    """Initialize project files in current directory."""


@add.command()
def assets(names: list[str]):
    print(f"Accepted names: {names}")


@add.command()
def capital(names: list[str]):
    print(f"Accepted names: {names}")


@add.command()
def liabilities(names: list[str]):
    print(f"Accepted names: {names}")


@add.command()
def income(names: list[str]):
    print(f"Accepted names: {names}")


@add.command()
def expenses(names: list[str]):
    print(f"Accepted names: {names}")


@add.command()
def labels(labels: list[str]):
    print(f"Accepted names: {labels}")


# @chart.command()
# def set_retained_earnings(name: str):
#     """Set retained earnings account."""
#     print(f"Accepted name: {name}")


@chart.command()
def name(name: str, title: str):
    """Set account title."""
    print(f"Renaming {name} to {title}.")


@chart.command()
def offset(name: str, contra_names: list[str]):
    """Add contra accounts."""
    print(f"Offsetting {name} with {contra_names}.")


@app.command()
def load(path: str):
    """Load starting balances from JSON file."""


@app.command()
def post(title: str, amount: Amount, debit: str, credit: str):
    """Post double entry."""


@app.command()
def post_compound(title: str, debits: list[str, Amount], credits: list[str, Amount]):
    """Post compound entry."""


@app.command()
def close():
    """Post closing entries."""


@app.command()
def report(
    trial_balance: bool = False,
    balance_sheet: bool = False,
    income_statement: bool = False,
    account_balances: bool = False,
    all: bool = False,
):
    """Show reports."""


@app.command(name="assert")
def assert_(name, balance: Amount):
    """Verify account balance."""


@app.command()
def unlink(
    yes: Annotated[bool, typer.Option(prompt="Are you sure you want to delete files?")]
):
    """Permanently delete project files in current directory."""
    if yes:
        print(f"Deleting files")
    else:
        print("Operation cancelled")


if __name__ == "__main__":
    app()
