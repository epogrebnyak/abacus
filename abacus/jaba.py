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
  jaba chart <chart_file> create <store_file> [--using <start_balances_file>]
  jaba names <name_file> touch
  jaba names <name_file> set <account_name> <title>
  jaba names <name_file> list
  jaba store <store_file> post <dr_account> <cr_account> <amount> [--adjust] [--post-close]
  jaba store <store_file> post --dr <dr_account> --cr <cr_account> --amount <amount> [--adjust] [--post-close]
  jaba store <store_file> close [--again]
  jaba store <store_file> list [--open | --business | --adjust | --close | --post-close | --is-closed]
  jaba report <store_file> (-i | --income-statement) [--names <name_file>] [--rich]
  jaba report <store_file> (-b | --balance-sheet) [--names <name_file>] [--rich]
  jaba report <store_file> (-t | --trial-balance) [--credit [--sum] | --debit [--sum]] [--all]
  jaba report <store_file> (-a | --account) <account_name> [--assert <amount>]
  jaba --args

Options:
  -h --help     Show this screen.
  --version     Show version.
  --args        Print arguments.
"""

import json
import sys
from pathlib import Path
from pprint import pprint
from typing import Dict, List

from docopt import docopt
from pydantic import BaseModel

from abacus import AbacusError, Amount, Chart, Journal


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class PreChart(BaseModel):
    """A class similar to Chart, but allowing empty fields.
    PreChart is used to gather parameters from command line interface
    and later create Chart."""

    assets: List[str] = []
    expenses: List[str] = []
    equity: List[str] = []
    retained_earnings_account: str | None = None
    liabilities: List[str] = []
    income: List[str] = []
    contra_accounts: Dict[str, List[str]] = {}
    # income_summary_account = "_profit"

    def to_file(self, path):
        Path(path).write_text(json.dumps(self.dict(), indent=2), encoding="utf-8")

    @classmethod
    def from_file(cls, path):
        return PreChart(**read_json(path))


def main():
    arguments = docopt(__doc__, version="0.4.3")
    if arguments["--args"]:
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
                pprint(chart.retained_earnings_account)
            if arguments["--capital"]:
                chart.equity = account_names  # rename 'equity' to "capital"
                pprint(chart.equity)
            for flag in ["--assets", "--income", "--expenses", "--liabilities"]:
                if arguments[flag]:
                    attr = flag[2:]
                    setattr(chart, attr, account_names)
                    pprint(getattr(chart, attr))
            chart.to_file(path)
        if arguments["offset"]:
            chart.contra_accounts[arguments["<account_name>"]] = arguments[
                "<contra_account_names>"
            ]
            pprint(chart.contra_accounts)
            chart.to_file(path)
        if arguments["validate"]:
            # Create Chart object and see what happens
            chart2 = Chart(**PreChart.from_file(path).dict())
            pprint(chart2.dict())
        if arguments["create"]:
            chart = Chart(**PreChart.from_file(path).dict())
            journal = chart.journal()
            if arguments["--using"]:  # FIXME: does not work
                starting_balances = read_json(arguments["<start_balances_file>"])
                journal = chart.journal(starting_balances)
            journal.save(arguments["<store_file>"])
            pprint(journal.data.dict())
    elif arguments["names"]:
        pass
    elif arguments["store"]:
        path = Path(arguments["<store_file>"])
        journal = Journal.load(path)
        if arguments["post"]:
            journal.post(
                dr=arguments["<dr_account>"],
                cr=arguments["<cr_account>"],
                amount=arguments["<amount>"],
            )
            journal.save(path)
        if arguments["close"]:
            if arguments["--again"]:
                journal.data.is_closed = False
            journal.close()
            journal.save(path)
        if arguments["list"]:
            show = journal.data.dict()
            # [--open | --business | --adjust | --close | --post-close]
            if arguments["--open"]:
                show = journal.data.accounts
            if arguments["--business"]:
                show = journal.data.business_entries
            if arguments["--adjust"]:
                show = ""
            if arguments["--close"]:
                show = journal.data.closing_entries
            if arguments["--is-closed"]:
                show = journal.data.is_closed
            if arguments["--post-close"]:
                show = ""
            pprint(show)
    elif arguments["report"]:
        path = Path(arguments["<store_file>"])
        journal = Journal.load(path)
        if arguments["-i"] or arguments["--income-statement"]:
            pprint(journal.income_statement().__dict__)
        if arguments["-b"] or arguments["--balance-sheet"]:
            pprint(journal.balance_sheet().__dict__)
        if arguments["-t"] or arguments["--trial-balance"]:
            if arguments["--all"]:
                pprint(journal.balances().data)
            else:
                pprint(journal.nonzero_balances().data)
        if arguments["-a"] or arguments["--account"]:
            account_name = arguments["<account_name>"]
            actual = journal.balances().data[account_name]
            if arguments["--assert"]:
                amount = Amount(arguments["<amount>"])
                if actual != amount:
                    raise AbacusError([account_name, actual, amount])
            pprint(actual)
    elif arguments["names"]:
        raise NotImplementedError  # yet


if __name__ == "__main__":
    main()
