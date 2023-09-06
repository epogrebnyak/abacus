import click
from click_option_group import RequiredMutuallyExclusiveOptionGroup, optgroup


@click.group()
def bx():
    pass


@bx.group()
def chart():
    pass


@chart.command()
@optgroup.group("account_type", cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option("-a", "--assets")
@optgroup.option("-c", "--capital")
@optgroup.option("-l", "--liabilities")
@optgroup.option("-i", "--income")
@optgroup.option("-e", "--expenses")
def add(account_type):
    click.echo("Add accounts to chart")
    click.echo(account_type)


if __name__ == "__main__":
    bx()
