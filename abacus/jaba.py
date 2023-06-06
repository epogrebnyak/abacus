"""
jaba is a minimal accounting manager.

Usage:
  jaba chart <chart_file> create
  jaba chart <chart_file> set --assets <account_names>...
  jaba chart <chart_file> set --expenses <account_names>... 
  jaba chart <chart_file> set --capital <account_names>...
  jaba chart <chart_file> set [--re | --retained-earnings] <account_name>
  jaba chart <chart_file> set --liabilities <account_names>...
  jaba chart <chart_file> set --income <account_names>...
  jaba chart <chart_file> offset <contra_account_names>... --contra <account_name>
  jaba chart <chart_file> validate
  jaba chart <chart_file> list
  jaba names <name_file> create
  jaba names <name_file> set <account_name> <title>
  jaba names <name_file> list
  jaba store <store_file> <chart_file> create [--using <start_balances_file>]
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

import sys
from docopt import docopt
from pathlib import Path
from pprint import pprint
from abacus.chart import Chart
from typing import List, Dict
import json

from pydantic import BaseModel
from dataclasses import field


class PreChart(BaseModel):
    assets: List[str] = []
    expenses: List[str] = []
    equity: List[str] = []
    retained_earnings_account: str = ""
    liabilities: List[str] = []
    income: List[str] = []
    contra_accounts: Dict[str, List[str]] = {}
    income_summary_account = "_profit"

    def to_file(self, path):
        Path(path).write_text(json.dumps(self.dict(), indent=2), encoding="utf-8")

    @classmethod
    def from_file(cls, path):
        return PreChart(**json.loads(Path(path).read_text(encoding="utf-8")))


def main():
    arguments = docopt(__doc__, version="0.4.3")
    print(arguments)
    if arguments["chart"]:
        path = Path(arguments["<chart_file>"])
        if arguments["create"]:
            if path.exists():
                sys.exit(f"Cannot create chart, file {path} already exists.")
            chart = PreChart()
            chart.to_file(path)
            pprint(chart)
        chart = PreChart.from_file(path)
        if arguments["set"]:
            account_names = arguments["<account_names>"]
            if arguments["--re"] or arguments["--retained-earnings"]:
                chart.retained_earnings = arguments["<account_name>"]
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
        if arguments["list"]:
            chart = PreChart.from_file(path)
            pprint(chart.dict())
    elif arguments["names"]:
        pass
    elif arguments["store"]:
        pass


if __name__ == "__main__":
    main()
