"""Utility for double-entry bookkeeping and financial reporting.

Usage:
  cx init  
  cx name <account> <title>
  cx post --debit <debit_account> --credit <credit_account> --amount <amount>
  cx close
  cx report --trial-balance
  cx report --balance-sheet [--rich | --json]
  cx report --income-statement [--rich | --json]
  cx delete <file>

Options:
  -h, --help                 Show this screen.
  --debit <debit_account>    Provide debit account name for entry.
  --credit <credit_account>  Provide credit account name for entry.
  --amount <amount>          Provide transaction amount for entry.
  --rich                     Print report in a nice colored format.      
  --json                     Emit report in JSON format.         
"""
# NOTE: add/add breaks the workflow
# сx add (--asset | --capital | --liability | --expense | --income) <account_names>...
# сx adds (--asset | --capital | --liability | --expense | --income) <account_name> [--title <title>]
# cx offset <account_name> <contra_account_names>...
# cx account --balances
# cx assert cash 200
# cx export --excel <file>

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from docopt import docopt

from abacus.experimental.chart_command import (
    ChartCommand,
    LedgerCommand,
    report_command,
)


def cwd() -> Path:
    return Path(os.getcwd())


@dataclass
class PathFinder:
    directory: Path

    @property
    def chart(self):
        return self.directory / "chart.json"

    @property
    def entries(self):
        return self.directory / "entries.csv"


def last(string):
    return string.split(":")[-1]


def dispatch_commands(arguments: Dict):
    chart_path = PathFinder(directory=cwd()).chart
    ledger_path = PathFinder(directory=cwd()).entries
    if arguments["init"]:
        ChartCommand.new().write(chart_path).echo()
        LedgerCommand.start_ledger(ledger_path).echo()
    elif arguments["post"]:
        # split debit and credit account names and  add to chart if needed
        (
            ChartCommand.read(chart_path)
            .promote(arguments["--debit"])
            .promote(arguments["--credit"])
            .write(chart_path)
        )
        # post to entries store
        dr = last(arguments["--debit"])
        cr = last(arguments["--credit"])
        amount = arguments["--amount"]
        LedgerCommand.read(ledger_path).post_entry(dr, cr, amount)
    elif arguments["name"]:
        (
            ChartCommand.read(chart_path)
            .set_name(arguments["<account>"], arguments["<title>"])
            .echo()
            .write(chart_path)
        )
    elif arguments["close"]:
        chart = ChartCommand.read(chart_path).chart
        LedgerCommand.read(ledger_path).post_closing_entries(chart)
    elif arguments["delete"]:
        path = Path(arguments["<file>"])
        if path.exists():
            path.unlink()
            print(f"Deleted file: {path}")
    elif arguments["report"]:
        report_command(arguments, ledger_path, chart_path)
    else:
        sys.exit("Command not recognized. Use 'cx --help' for reference.")


def main():
    arguments = docopt(__doc__, version="0.7.0")
    dispatch_commands(arguments)
