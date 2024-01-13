import click


@click.command(name="post")
@click.option("--entry", type=(str, str, int), multiple=True)
@click.option("--debit", type=(str, int), multiple=True)
@click.option("--credit", type=(str, int), multiple=True)
@click.option("--strict", is_flag=True, default=False)
def postx(entry, debit, credit, strict):
    """Post accounting entries to ledger."""
    print(entry)
    print(debit)
    print(credit)
    print(strict)


#    chart = get_chart()
#    store = get_store()
#    entries = CompoundEntry(debits=debit, credits=credit).to_entries(chart.null_account)
#    store.append_many(entries)
