import shlex

from docopt import docopt

import abacus.experimental.cx as cx
from abacus.experimental.chart_command import ChartCommand


def test_chart_command(tmp_path):
    tmp_path = tmp_path / "chart.json"
    ChartCommand.new().promote("asset:cash").write(tmp_path)
    ChartCommand.new().promote("asset:cash").write(tmp_path)
    ChartCommand.read(tmp_path).promote("cash").write(tmp_path)
    ChartCommand.read(tmp_path).promote("expense:ads").write(tmp_path)
    ChartCommand.read(tmp_path).promote("ads").write(tmp_path)
    ChartCommand.read(tmp_path).promote("capital:equity").write(tmp_path)
    ChartCommand.read(tmp_path).promote("contra:equity:withdrawals").write(tmp_path)
    ChartCommand.read(tmp_path).promote("contra:equity:treasury_stock").write(tmp_path)
    assert ChartCommand.read(tmp_path).chart.json(indent=2)


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
cx delete entries.csv
cx delete chart.json"""


def test_cx_script():
    for line in script.split("\n"):
        argv = shlex.split(line)
        arguments = docopt(cx.__doc__, argv[1:])
        cx.dispatch_commands(arguments)