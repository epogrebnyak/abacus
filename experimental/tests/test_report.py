from typing import Dict

from engine.accounts import Asset
from engine.base import Entry
from engine.chart import Chart
from engine.ledger import Ledger
from engine.report import BalanceSheet
from pydantic import BaseModel  # type: ignore


class BalanceSheet2(BaseModel):
    assets: Dict[str, int]

    @classmethod
    def _s(cls, ledger):
        return BalanceSheet2(assets=ledger.subset(Asset).balances())


def test_create_balance_sheet():
    chart = Chart(assets=["cash"], equity=["equity"])
    ledger = Ledger.new(chart).post(Entry("cash", "equity", 1000))
    assert ledger.balance_sheet(chart) == BalanceSheet(
        assets={"cash": 1000}, capital={"equity": 1000, "re": 0}, liabilities={}
    )

    # print("Works fine      ", ledger.subset(Asset))
    # print("Works fine again", ledger.subset(Asset))
    # # BalanceSheet2 and BalanceSheet3 have identical code
    # # BalanceSheet2 is local, BalanceSheet3 is imported
    # print("Does work:      ", BalanceSheet2._s(ledger))  # assets={'cash': 1000}
    # print("Does NOT work   ", BalanceSheet3._s(ledger))  # assets={}
    # assert BalanceSheet2._s(ledger) == BalanceSheet3._s(ledger)
    # # 1. Why is the result BalanceSheet2 and BalanceSheet3 different?
    # # 2. How to make BalanceSheet3 assets={'cash': 1000}?
