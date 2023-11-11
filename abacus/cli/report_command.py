from pathlib import Path

from abacus import Chart, Ledger, LineJSON


def current(entries_path: Path, chart_path: Path):
    chart = Chart.parse_file(chart_path)
    store = LineJSON(entries_path)
    ledger = chart.ledger()
    return chart, store, ledger


def trial_balance(entries_path: Path, chart_path: Path):
    chart = Chart.parse_file(chart_path)
    ledger = current_ledger(chart_path, entries_path)
    return ledger.trial_balance(chart)


def balance_sheet(entries_path: Path, chart_path: Path):
    chart = Chart.parse_file(chart_path)
    ledger = current_ledger(chart_path, entries_path)
    return ledger.balance_sheet(chart)


def income_statement(entries_path: Path, chart_path: Path):
    chart, store, ledger = current(entries_path, chart_path)
    entries = store.yield_entries_for_income_statement(chart)
    return ledger.post_many(entries).income_statement(chart)


def account_balances(entries_path: Path, chart_path: Path, nonzero: bool):
    ledger = current_ledger(entries_path=entries_path, chart_path=chart_path)
    if nonzero:
        return ledger.nonzero_balances()
    else:
        return ledger.balances()


def current_ledger(chart_path: Path, entries_path: Path) -> Ledger:
    chart = Chart.parse_file(chart_path)
    entries = LineJSON(entries_path).yield_entries()
    return chart.ledger().post_many(entries)


def print_statement(plain, json, rich, statement, chart):
    if json:
        print(statement.json())
    elif rich:
        statement.print_rich(chart.names)
    elif plain:
        print(statement.__cls__.__name__.capitalize())
        print(statement.view(chart.names))
