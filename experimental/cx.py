script = """cx new "Joan Law Office (Weygandt, ed 12, p. 31)"
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
cx close
cx name ar "Accounts receivable"
cx report --balance-sheet
cx report --income-statement
cx chart --json"""

from pathlib import Path
import os
from chart_command import init_chart

def match_type(prefix):
    types = (Asset, Expense, Income, Liability, Capital)
    for t in types:
        if prefix in [t.__name__, t.__name__.lower()]:
            return t    


def split_on_colon(text):
    parts = "contra:equity:withdrawal".split(":")
    if parts[0] == "contra":
        return (Contra, parts[1:])

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
    if arguments["new"]:
        init_chart(path=PathFinder(directory=cwd()).chart)
    elif arguments["post"]:
        # split debit and credit account names, add to chart if needed
        # exit if account name not valid (not prefix for new account)
    elif arguments["name"]:
        print("name")
    elif arguments["chart"]:
        print("chart")
    elif arguments["report"]:
        print("report")

docstring = """Usage:
  cx new <title> [--chart-file=<chart-file>]
  cx post --debit <debit_account> --credit <credit_account> --amount <amount>
  cx name <account> <title>
  cx chart
  cx report --balance-sheet
  cx report --income-statement
"""

from docopt import docopt
import shlex

for line in script.split("\n"):
    print(line)
    argv = shlex.split(line)
    print(argv)
    arguments = docopt(docstring, argv[1:])
    commands(arguments)
