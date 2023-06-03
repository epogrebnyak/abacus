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
        equity=["shares", "re"],
        liabilities=[],
        income=["sales"],
        contra_accounts={
            "sales": (["discounts", "returns"], "net_sales"),
            "shares": (["treasury_shares"], "shares_outstanding"),
            "ppe": (["depr"], "net_ppe"),
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
        "discounts": ContraIncome(debits=[], credits=[]),
        "returns": ContraIncome(debits=[], credits=[]),
        "treasury_shares": ContraCapital(debits=[], credits=[]),
        "depr": ContraAsset(debits=[], credits=[]),
        "_profit": IncomeSummaryAccount(debits=[], credits=[]),
    }
