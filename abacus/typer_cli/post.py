"""Post entries to ledger."""
from pathlib import Path

import click

from abacus.base import AbacusError
from abacus.core import CompoundEntry
from abacus.typer_cli.base import get_chart, get_store, last
from abacus.typer_cli.ledger import load, post
from abacus.user_chart import UserChart


def post_compound(debits, credits, title, chart_file, store_file):
    for label, _ in debits + credits:
        user_chart = UserChart.load(chart_file)
        if ":" in label:
            try:
                user_chart.use(label)
            except AbacusError:
                pass
        user_chart.save()
    debits = [(last(name), value) for name, value in debits]
    credits = [(last(name), value) for name, value in credits]
    compound_entry = CompoundEntry(debits=debits, credits=credits)
    chart = get_chart(chart_file)
    entries = compound_entry.to_entries(chart.null_account)
    store = get_store(store_file)
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
@click.option(
    "--starting-balances-file", type=Path, help="Load starting balances from JSON file."
)
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
    title,
    entry,
    debit,
    credit,
    strict,
    starting_balances_file,
    chart_file,
    store_file,
    verbose,
):
    """Post accounting entries to ledger."""
    if starting_balances_file:
        print(f"Loading starting balances from {starting_balances_file}...")
        load(starting_balances_file, chart_file, store_file)
    if entry:
        for item in entry:
            dr, cr, amount = item
            post(dr, cr, amount, title, chart_file, store_file)
    if debit or credit:
        post_compound(debit, credit, title, chart_file, store_file)
    if strict:
        print("In strict mode `abacus` will assume:")
        print("- all used account names are already in chart.")
        print("Flag was set to:", strict)
    if verbose:
        print("Chart file:", chart_file)
        print("Store file:", store_file)
