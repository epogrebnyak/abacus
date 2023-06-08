"""
*jaba* is a minimal double entry accounting manager that can define a chart of accounts,
open ledger, post entries, close accounts at period end and produce balance sheet 
and income statement reports. *jaba* is aware of contra accounts, can do a trail balance
and add adjustment and post-close entries.

Usage:
  jaba chart <chart_file> touch
  jaba chart <chart_file> set --assets <account_names>...
  jaba chart <chart_file> set --expenses <account_names>... 
  jaba chart <chart_file> set --capital <account_names>...
  jaba chart <chart_file> set [--re | --retained-earnings] <account_name>
  jaba chart <chart_file> set --liabilities <account_names>...
  jaba chart <chart_file> set --income <account_names>...
  jaba chart <chart_file> offset <account_name> <contra_account_names>...
  jaba chart <chart_file> validate
  jaba chart <chart_file> list
  jaba chart <chart_file> create <store_file> [--balances <start_balances_file>]
  jaba names <name_file> touch
  jaba names <name_file> set <account_name> <title>
  jaba names <name_file> list
  jaba store <store_file> post <dr_account> <cr_account> <amount> [--adjust] [--post-close]
  jaba store <store_file> close --all
  jaba store <store_file> list [--head <n> | --tail <n> | --last]
  jaba store <store_file> list [--open | --business | --adjust | --close | --post-close]
  jaba store <store_file> report (-i | --income-statement) [--names <name_file>]
  jaba store <store_file> report (-b | --balance-sheet) [--names <name_file>]
  jaba store <store_file> balances [--credit [--sum] | --debit [--sum]] 
  jaba store <store_file> balance <account_name>

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

# jaba store <store_file> <chart_file> close (--contra-income --contra-expenses)
# jaba store <store_file> <chart_file> close (--income --expenses)
# jaba store <store_file> <chart_file> close (--isa | --income-summary-account)

import json
import sys
from pathlib import Path
from pprint import pprint
from typing import Dict, List

from docopt import docopt
from pydantic import BaseModel

from abacus.chart import Chart


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class PreChart(BaseModel):
    assets: List[str] = []
    expenses: List[str] = []
    equity: List[str] = []
    retained_earnings_account: str | None = None
    liabilities: List[str] = []
    income: List[str] = []
    contra_accounts: Dict[str, List[str]] = {}
    income_summary_account = "_profit"

    def to_file(self, path):
        Path(path).write_text(json.dumps(self.dict(), indent=2), encoding="utf-8")

    @classmethod
    def from_file(cls, path):
        return PreChart(**read_json(path))


def main():
    arguments = docopt(__doc__, version="0.4.3")
    print(arguments)
    if arguments["chart"]:
        path = Path(arguments["<chart_file>"])
        if arguments["touch"]:
            if path.exists():
                sys.exit(f"Cannot create chart, file {path} already exists.")
            chart = PreChart()
            chart.to_file(path)
            pprint(chart.dict())
        chart = PreChart.from_file(path)
        if arguments["set"]:
            account_names = arguments["<account_names>"]
            if arguments["--re"] or arguments["--retained-earnings"]:
                chart.retained_earnings_account = arguments["<account_name>"]
            if arguments["--capital"]:
                chart.equity = account_names  # rename 'equity' to "capital"
            for flag in ["--assets", "--income", "--expenses", "--liabilities"]:
                if arguments[flag]:
                    attr = flag[2:]
                    setattr(chart, attr, account_names)
            chart.to_file(path)
            pprint(chart.dict())
        if arguments["offset"]:
            chart.contra_accounts[arguments["<account_name>"]] = arguments[
                "<contra_account_names>"
            ]
            chart.to_file(path)
            pprint(chart.dict())
        if arguments["validate"]:
            # Create Chart object and see what happens
            chart2 = Chart(**PreChart.from_file(path).dict())
            pprint(chart2.dict())
        if arguments["create"]:
            chart = Chart(**PreChart.from_file(path).dict())
            journal = chart.journal()
            if arguments["--balances"]:
                starting_balances = read_json(arguments["starting_balances_file"])
                journal = journal.start(starting_balances)
            journal.save(arguments["<store_file>"])
            pprint(journal.dict())
    elif arguments["names"]:
        pass
    elif arguments["store"]:
        pass


"""
-- testing of a multiline string pytest-console-plugin
-- extract console code from README
-- names class
-- store details
-- ...  
"""
if __name__ == "__main__":
    main()
