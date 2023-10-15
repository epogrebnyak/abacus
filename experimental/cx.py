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
  --title <title>            Provide longer account name (title).             
"""
# FIXME: add/add breaks the workflow
# сx add (--asset | --capital | --liability | --expense | --income) <account_names>...
# сx adds (--asset | --capital | --liability | --expense | --income) <account_name> [--title <title>]
# cx offset <account_name> <contra_account_names>...
# cx account --balances
# cx assert cash 200
# cx export --excel <file>

import os
import shlex
from dataclasses import dataclass
from pathlib import Path

from chart_command import ChartCommand, LedgerCommand, report_command
from docopt import docopt


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


def dispatch_commands(arguments):
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
        Path(arguments["<file>"]).unlink()
    elif arguments["report"]:
        report_command(arguments, ledger_path, chart_path)


# cx add --asset cash ar equipment
# cx add --liability ap note
# cx adds --capital equity --title "Equity less withdrawals"
# cx offset equity withdrawal
# cd add --expense rent salaries utilities ads
# cx add --income sales
script = """cx init
cx post --debit asset:cash               --credit capital:equity --amount 11000
cx post --debit expense:rent             --credit cash           --amount 800
cx post --debit asset:equipment          --credit liability:ap   --amount 3000
cx post --debit cash                     --credit income:sales   --amount 1500
cx post --debit cash                     --credit liability:note --amount 700
cx post --debit asset:ar                 --credit sales          --amount 2000
cx post --debit expense:salaries         --credit cash           --amount 500
cx post --debit expense:utilities        --credit cash           --amount 300
cx post --debit expense:ads              --credit cash           --amount 100
cx post --debit contra:equity:withdrawal --credit cash           --amount 1000
cx name ar "Accounts receivable"
cx name ap "Accounts payable"
cx name ads "Advertising"
cx report --trial-balance
cx close
cx report --balance-sheet --rich
cx report --income-statement
cx delete entries.csv"""

for line in script.split("\n"):
    argv = shlex.split(line)
    arguments = docopt(__doc__, argv[1:])
    dispatch_commands(arguments)
