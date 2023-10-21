import click
#import click_default_group
from abacus import Entry, Amount

@click.group()
def cli():
    pass

@cli.command()
def init():
    """Initialize chart and ledger in current folder."""
    click.echo('Initialized the ledger')

@cli.command()
@click.option('--debit', required=True, type=str, help='Debit account name.')
@click.option('--credit', required=True, type=str, help='Credit account name.')
@click.option('--amount', required=True, type=int, help='Transaction amount.')
def post(debit, credit, amount):
    """Post entry to ledger."""
    click.echo(Entry(debit, credit, Amount(amount)))

@cli.command()
@click.argument('what', type=click.Choice(['MD5', 'SHA1'], case_sensitive=False))
def close():
    """Close ledger at period end."""

from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup

@cli.command()
@click.argument('type_', type=click.Choice(['trial-balance', 'balance-sheet', 'income-statement'], case_sensitive=False))
@optgroup.group('Modify output', cls=RequiredMutuallyExclusiveOptionGroup,
                help='Show reports as JSON or rich text.')
@optgroup.option('--json', is_flag=True, mutually_exclusive=True, help='Show JSON format.')
@optgroup.option('--rich', is_flag=True, mutually_exclusive=True, help='Show with rich text formatting.')


def report(type_, json_, rich):
    """Show trial balace, balance sheet or income statement."""
    click.echo(type_, json_, rich)


#   cx init  
#   cx name <account> <title>
#   cx post --debit <debit_account> --credit <credit_account> --amount <amount>
#   cx close
#   cx report --trial-balance
#   cx report --balance-sheet [--rich | --json]
#   cx report --income-statement [--rich | --json]
#   cx delete <file>


if __name__ == '__main__':
    cli()

