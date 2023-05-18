from abacus import Chart, Entry, RE
from abacus.accounts import Asset, Capital, IncomeSummaryAccount, RetainedEarnings
from abacus.ledger import Ledger, safe_process_postings


def test_make_ledger():
    _chart = Chart(
        assets=["cash"],
        equity=["equity", RE("re")],
        income=[],
        expenses=[],
        liabilities=[],
    )
    assert _chart.make_ledger() == {
        "cash": Asset(debits=[], credits=[]),
        "equity": Capital(debits=[], credits=[]),
        "_profit": IncomeSummaryAccount(debits=[], credits=[]),
        "re": RetainedEarnings(debits=[], credits=[], netting=None),
    }


def test_safe_process_entries():
    _ledger = Ledger(
        {
            "cash": Asset(debits=[], credits=[]),
            "equity": Capital(debits=[], credits=[]),
        }
    )
    _, _failed = safe_process_postings(_ledger, [Entry("", "", 0)])
    assert _failed == [Entry("", "", 0)]
