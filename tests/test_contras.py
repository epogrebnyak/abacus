# %%

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
    assets=["cash", "ppe"],
    expenses=[],
    equity=["shares"],
    retained_earnings_account="re",
    liabilities=[],
    income=["sales"],
    contra_accounts={
        "sales": ["discounts", "returns"],
        "shares": ["treasury_shares"],
        "ppe": ["depr"],
    },
)


def test_make_ledger_with_netting():
    chart = Chart(
        assets=["cash", "ppe"],
        expenses=[],
        equity=["shares"],
        retained_earnings_account="re",
        liabilities=[],
        income=["sales"],
        contra_accounts={
            "sales": ["discounts", "returns"],
            "shares": ["treasury_shares"],
            "ppe": ["depr"],
        },
    )
    ledger = chart.ledger()
    assert ledger == {
        "cash": Asset(debits=[], credits=[]),
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
        "discounts": ContraIncome(link="sales", debits=[], credits=[]),
        "returns": ContraIncome(link="sales", debits=[], credits=[]),
        "treasury_shares": ContraCapital(link="shares", debits=[], credits=[]),
        "depr": ContraAsset(link="ppe", debits=[], credits=[]),
        "_profit": IncomeSummaryAccount(debits=[], credits=[]),
    }
