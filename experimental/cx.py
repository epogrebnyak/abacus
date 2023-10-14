import os
import shlex
from dataclasses import dataclass
from pathlib import Path

from chart_command import ChartCommand, LedgerCommand, report_command
from docopt import docopt

script = """cx init
cx post --debit asset:cash               --credit capital:equity --amount 11000
cx post --debit expense:rent             --credit cash           --amount 800
cx post --debit asset:equipment          --credit cash           --amount 3000
cx post --debit cash                     --credit income:sales   --amount 1500
cx post --debit cash                     --credit liability:note --amount 700
cx post --debit asset:ar                 --credit sales          --amount 2000
cx post --debit expense:salaries         --credit cash           --amount 2000
cx post --debit expense:utilities        --credit cash           --amount 300
cx post --debit expense:ads              --credit cash           --amount 100
cx post --debit contra:equity:withdrawal --credit cash           --amount 1000
cx name ar "Accounts receivable"
cx name ads "Advertising"
cx name equity "Equity less withdrawals"
cx report --trial-balance
cx close
cx report --balance-sheet --rich
cx report --income-statement
cx remove entries.csv"""

# move to tests
# ChartCommand.new().promote("asset:cash").write("chart.json")
# ChartCommand.new().promote("asset:cash").write("chart.json")
# ChartCommand.read("chart.json").promote("cash").write("chart.json")
# ChartCommand.read("chart.json").promote("expense:ads").write("chart.json")
# ChartCommand.read("chart.json").promote("ads").write("chart.json")
# ChartCommand.read("chart.json").promote("capital:equity").write("chart.json")
# ChartCommand.read("chart.json").promote("contra:equity:withdrawals").write("chart.json")
# ChartCommand.read("chart.json").promote("contra:equity:treasury_stock").write(
#     "chart.json"
# )
# ChartCommand.read("chart.json").chart.json(indent=2)


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


def commands(arguments):
    chart_path = PathFinder(directory=cwd()).chart
    ledger_path = PathFinder(directory=cwd()).entries
    if arguments["init"]:
        ChartCommand.new().write(chart_path).echo()
        LedgerCommand.start_ledger(ledger_path).echo()
    elif arguments["post"]:
        # split debit and credit account names, add to chart if needed
        # exit if account name not valid
        (
            ChartCommand.read(chart_path)
            .promote(arguments["<debit_account>"])
            .promote(arguments["<credit_account>"])
            .write(chart_path)
        )
        dr = arguments["<debit_account>"].split(":")[-1]
        cr = arguments["<credit_account>"].split(":")[-1]
        LedgerCommand.read(ledger_path).post_entry(dr, cr, arguments["<amount>"])
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
    # elif arguments["ledger"] and arguments["show"]:
    #    LedgerCommand.read(ledger_path).show()
    elif arguments["remove"]:
        Path(arguments["<file>"]).unlink()
    # elif arguments["chart"] and arguments["show"]:
    #    print(ChartCommand.read(chart_path).chart.json(indent=2))
    elif arguments["report"]:
        report_command(arguments, ledger_path, chart_path)


docstring = """Usage:
  cx init
  cx post --debit <debit_account> --credit <credit_account> --amount <amount>
  cx close
  cx name <account> <title>
  cx report (-t | --trial-balance)
  cx report (-b | --balance-sheet) [--rich | --json]
  cx report (-i | --income-statement) [--rich | --json]
  cx remove <file>
"""
#  cx export --excel <file>

for line in script.split("\n"):
    argv = shlex.split(line)
    arguments = docopt(docstring, argv[1:])
    commands(arguments)
