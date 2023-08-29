from ledger import Ledger
from chart import Chart
from base import Entry
from accounts import Asset, Capital, Liability
from report import BalanceSheet3
from dataclasses import dataclass
from typing import Dict
from pydantic import BaseModel  # pylint: disable=import-error # type: ignore


class BalanceSheet2(BaseModel):
    assets: Dict[str, int]

    @classmethod
    def _s(cls, ledger):
        return BalanceSheet2(assets=ledger.subset(Asset).balances())


chart = Chart(assets=["cash"], equity=["equity"])
ledger = Ledger.new(chart).post(Entry("cash", "equity", 1000))
print("Works fine      ", ledger.subset(Asset))
print("Works fine again", ledger.subset(Asset))
# BalanceSheet2 and BalanceSheet3 have identical code
# BalanceSheet2 is local, BalanceSheet3 is imported
print("Does work:      ", BalanceSheet2._s(ledger))  # assets={'cash': 1000}
print("Does NOT work   ", BalanceSheet3._s(ledger))  # assets={}
assert BalanceSheet2._s(ledger) == BalanceSheet3._s(ledger)
# 1. Why is the result BalanceSheet2 and BalanceSheet3 different?
# 2. How to make BalanceSheet3 assets={'cash': 1000}?
