from abacus import Chart, Entry
from abacus.accounts import (
    Asset,
    Capital,
    ContraAsset,
    ContraCapital,
    ContraIncome,
    Expense,
    Income,
    IncomeSummaryAccount,
    RetainedEarnings,
)
from abacus.ledger import Ledger, safe_process_postings


def test_make_ledger():
    _chart = Chart(
        assets=["cash"],
        equity=["equity"],
    ).set_retained_earnings("re")
    assert _chart.ledger() == {
        "cash": Asset(debits=[], credits=[]),
        "equity": Capital(debits=[], credits=[]),
        "_profit": IncomeSummaryAccount(debits=[], credits=[]),
        "re": RetainedEarnings(debits=[], credits=[]),
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


def test_create_ledger_again():
    (
        Chart(
            assets=["cash", "goods", "ppe"],
            equity=["equity", "re"],
            income=["sales"],
            expenses=["cogs", "sga"],
        )
        .set_retained_earnings("re")
        .offset("ppe", ["depreciation"])
        # https://stripe.com/docs/revenue-recognition/methodology
        .offset("sales", ["refunds", "voids"])
        .ledger()
    ) == {
        "cash": Asset(debits=[], credits=[]),
        "goods": Asset(debits=[], credits=[]),
        "ppe": Asset(debits=[], credits=[]),
        "cogs": Expense(debits=[], credits=[]),
        "sga": Expense(debits=[], credits=[]),
        "equity": Capital(debits=[], credits=[]),
        "sales": Income(debits=[], credits=[]),
        "re": RetainedEarnings(debits=[], credits=[]),
        "_profit": IncomeSummaryAccount(debits=[], credits=[]),
        "depreciation": ContraAsset(debits=[], credits=[]),
        "refunds": ContraIncome(debits=[], credits=[]),
        "voids": ContraIncome(debits=[], credits=[]),
    }


def test_make_ledger_with_netting():
    chart = Chart(
        assets=["ppe"], expenses=[], equity=["shares"], liabilities=[], income=["sales"]
    ).set_retained_earnings("re")
    chart.contra_accounts = {
        "sales": ["refunds", "voids"],
        "shares": ["treasury_shares"],
        "ppe": ["depreciation"],
    }
    ledger = chart.ledger()
    assert ledger == {
        "ppe": Asset(
            debits=[],
            credits=[],
        ),
        "shares": Capital(
            debits=[],
            credits=[],
        ),
        "re": RetainedEarnings(debits=[], credits=[]),
        "sales": Income(debits=[], credits=[]),
        "refunds": ContraIncome(debits=[], credits=[]),
        "voids": ContraIncome(debits=[], credits=[]),
        "treasury_shares": ContraCapital(debits=[], credits=[]),
        "depreciation": ContraAsset(debits=[], credits=[]),
        "_profit": IncomeSummaryAccount(debits=[], credits=[]),
    }
