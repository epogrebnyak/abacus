import click

from abacus import Amount, Entry


@click.group()
def cli():
    pass


@cli.command()
@click.argument("account_name")
@click.option(
    "--title", type=str, required=False, help="Descriptive title for an account."
)
def add(account_name, title):
    """Add or rename account in chart.

    Examples:
      abacus add asset:cash --title "Cash and equivalents"
      abacus add expense:rent
      abacus add asset:ppe --title "Property, plant and equipment"
      abacus add contra:ppe:depreciation --title "Accumulated depreciation" """
    click.echo(account_name)
    click.echo(title)


@cli.command()
def init():
    """Initialize chart and ledger in current folder."""
    click.echo("Initialized the ledger")


@cli.command()
@click.option("--debit", required=True, type=str, help="Debit account name.")
@click.option("--credit", required=True, type=str, help="Credit account name.")
@click.option("--amount", required=True, type=int, help="Transaction amount.")
def post(debit, credit, amount):
    """Post entry to ledger."""
    click.echo(Entry(debit, credit, Amount(amount)))


@cli.command()
def close():
    """Close ledger at period end."""
    click.echo("Posted closing entries to ledger.")


@cli.command()
@click.argument(
    "type_",
    type=click.Choice(
        ["trial-balance", "balance-sheet", "income-statement"], case_sensitive=False
    ),
)
@click.option(
    "--plain/--rich",
    default=True,
    help="Choose plain or rich text output format [default: --plain].",
)
@click.option("--json", is_flag=True, help="Provide output as JSON.")
def report(type_, plain, json):
    """Print trial balace, balance sheet or income statement."""
    click.echo(type_)
    click.echo(plain)
    click.echo(json)


@cli.command()
@click.argument("what", type=click.Choice(["chart", "ledger"]), required=True)
@click.option(
    "--last",
    type=int,
    default=1,
    help="Number of last entries to show in ledger [default: 1].",
)
def show(what, last):
    """Print chart or ledger."""
    click.echo(f"Showing {what}.")
    click.echo(last)


@cli.command(name="account", help="Verify account balance.")
@click.argument("account_name")
@click.option("--assert-balance", type=int, help="Expected account balance.")
def assert_command(account_name, assert_balance):
    click.echo(account_name)
    click.echo(assert_balance)


@cli.command()
@click.argument("what", type=click.Choice(["chart", "ledger"]), required=True)
@click.confirmation_option(
    prompt="Are you sure you want to permanently delete this file?"
)
def unlink(what):
    """Delete chart or ledger in current folder."""
    click.echo(f"Deleted {what}.")


if __name__ == "__main__":
    cli()
