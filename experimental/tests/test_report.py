from engine.base import Entry
from engine.chart import Chart
from engine.ledger import Ledger
from engine.report import BalanceSheet


def test_create_balance_sheet():
    chart = Chart(assets=["cash"], equity=["equity"])
    ledger = Ledger.new(chart).post(Entry("cash", "equity", 1000))
    assert ledger.balance_sheet(chart) == BalanceSheet(
        assets={"cash": 1000}, capital={"equity": 1000, "re": 0}, liabilities={}
    )
