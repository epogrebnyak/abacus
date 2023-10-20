import sys
from pathlib import Path
from typing import Dict

from abacus import Chart, Ledger, LineJSON


def report_command(arguments: Dict, entries_path: Path, chart_path: Path):
    chart = Chart.parse_file(chart_path)
    store = LineJSON(entries_path)
    ledger = Ledger.new(chart)
    if arguments["--trial-balance"]:
        entries = store.yield_entries()
        ledger.post_many(entries)
        print(ledger.trial_balance(chart))
        sys.exit(0)
    if arguments["--balance-sheet"]:
        entries = store.yield_entries()
        ledger.post_many(entries)
        statement = ledger.balance_sheet(chart)
        title = "Balance sheet"
    elif arguments["--income-statement"]:
        entries = store.yield_entries_for_income_statement(chart)
        ledger.post_many(entries)
        statement = ledger.income_statement(chart)
        title = "Income statement"
    if arguments["--json"]:
        print(statement.json())
    elif arguments["--rich"]:
        statement.print_rich(chart.names)
    else:
        print(title)
        print(statement.view(chart.names))
