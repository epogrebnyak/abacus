from abacus.accounts import (
    Asset,
    Capital,
    ContraAsset,
    ContraCapital,
    ContraIncome,
    Income,
    IncomeSummaryAccount,
    RetainedEarnings,
)
from abacus.chart import Chart

chart = Chart(
    assets=["ppe"], expenses=[], equity=["shares"], liabilities=[], income=["sales"]
).set_retained_earnings("re")
chart.contra_accounts = {
    "sales": ["refunds", "voids"],
    "shares": ["treasury_shares"],
    "ppe": ["depreciation"],
}


def test_make_ledger_with_netting():
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
