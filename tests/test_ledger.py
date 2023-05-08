from abacus import Chart, Entry
from abacus.accounts import Asset, Capital, IncomeSummaryAccount
from abacus.chart import make_ledger
from abacus.ledger import Ledger, safe_process_entries


def test_make_ledger():
    _chart = Chart(
        assets=["cash"], equity=["equity"], income=[], expenses=[], liabilities=[]
    )
    assert make_ledger(_chart) == {
        "cash": Asset(debits=[], credits=[]),
        "equity": Capital(debits=[], credits=[]),
        "profit": IncomeSummaryAccount(debits=[], credits=[]),
    }


def test_safe_process_entries():
    _ledger = Ledger(
        {
            "cash": Asset(debits=[], credits=[]),
            "equity": Capital(debits=[], credits=[]),
            "profit": IncomeSummaryAccount(debits=[], credits=[]),
        }
    )
    _, _failed = safe_process_entries(_ledger, [Entry("", "", 0)])
    assert _failed == [Entry("", "", 0)]
