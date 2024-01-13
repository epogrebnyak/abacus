from pathlib import Path

import click

from abacus.core import CompoundEntry
from abacus.entries_store import LineJSON
from abacus.typer_cli.base import UserChartCLI, last
from abacus.typer_cli.ledger import load, post
from abacus.user_chart import UserChart


def post_compound(debits, credits, title, chart_file, store_file):
    for label, _ in debits + credits:
        if ":" in label:
            UserChart.load(chart_file).use(label).save()
    debits = [(last(name), value) for name, value in debits]
    credits = [(last(name), value) for name, value in credits]
    compound_entry = CompoundEntry(debits=debits, credits=credits)
    chart = UserChart.load(chart_file).chart()
    entries = compound_entry.to_entries(chart.null_account)
    store = LineJSON.load(store_file)
    store.append_many(entries)
    print("Posted compound entry:", compound_entry)
    print("Title:", title)


@click.command(name="post")
@click.option("--entry", type=(str, str, int), multiple=True, help="Post double entry,")
@click.option(
    "--debit", type=(str, int), multiple=True, help="Debit records for compound entry."
)
@click.option(
    "--credit",
    type=(str, int),
    multiple=True,
    help="Credit records for compound entry.",
)
@click.option("--starting-balances-file", type=Path, help="Load starting balances from JSON file.")
@click.option(
    "--strict",
    "-s",
    is_flag=True,
    default=False,
    help="Assure chart, ledger and accounts already exist.",
)
@click.option("--chart-file", type=Path)
@click.option("--store-file", type=Path)
@click.option(
    "--verbose", "-v", is_flag=True, default=False, help="Show more information."
)
@click.option("--title", "-t", type=str, help="Set transaction description.")
def postx(
    title, entry, debit, credit, strict, starting_balances_file, chart_file, store_file, verbose
):
    """Post accounting entries to ledger."""
    if starting_balances_file:
        print(f"Loading starting balances from {starting_balances_file}...")
        load(starting_balances_file, chart_file, store_file)

    if not strict:
        try:
            UserChartCLI.load(chart_file)
        except FileNotFoundError:
            from abacus.typer_cli.chart import init as chart_init

            chart_init()
    if not strict:
        if not LineJSON.load(store_file).path.exists():
            from abacus.typer_cli.ledger import init as ledger_init

            ledger_init()
    if entry:
        for item in entry:
            post(item[0], item[1], item[2], title, chart_file, store_file)
    if debit or credit:
        post_compound(debit, credit, title, chart_file, store_file)
    if strict:
        print("In strict mode `abacus` will assume:")
        print("- chart and ledger files already exist in project folder")
        print("- all used account names are already in chart.")
        print("Flag was set to:", strict)
    if verbose:
        print("Chart file:", chart_file)
        print("Store file:", store_file)
