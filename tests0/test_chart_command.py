import shlex

from click.testing import CliRunner

from abacus.cli.chart_command import ChartCommand
from abacus.cli.main import cx


def test_chart_command(tmp_path):
    tmp_path = tmp_path / "chart.json"
    ChartCommand(tmp_path).promote("asset:cash").write()
    ChartCommand(tmp_path).promote("asset:cash").write()
    ChartCommand.read(tmp_path).promote("cash").write()
    ChartCommand.read(tmp_path).promote("expense:ads").write()
    ChartCommand.read(tmp_path).promote("ads").write()
    ChartCommand.read(tmp_path).promote("capital:equity").write()
    ChartCommand.read(tmp_path).promote("contra:equity:withdrawals").write()
    ChartCommand.read(tmp_path).promote("contra:equity:treasury_stock").write()
    assert ChartCommand.read(tmp_path).json()


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
cx report -t
cx close
cx report --balance-sheet
cx report -b
cx report --income-statement
cx report -i
cx unlink --yes"""


def test_cx_script():
    runner = CliRunner()
    with runner.isolated_filesystem():
        for line in script.split("\n"):
            argv = shlex.split(line)[1:]
            print(argv)
            result = runner.invoke(cx, argv)
            assert result.exit_code == 0
