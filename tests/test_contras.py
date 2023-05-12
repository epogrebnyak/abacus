# %%

from abacus.accounts import (
    Asset,
    Capital,
    ContraAsset,
    ContraCapital,
    ContraIncome,
    Income,
    IncomeSummaryAccount,
    Netting,
)
from abacus.chart import Chart, make_ledger

chart = Chart(
    assets=["cash", "ppe"],
    expenses=[],
    equity=["shares"],
    liabilities=[],
    income=["sales"],
    contra_accounts={
        "sales": (["discounts", "returns"], "net_sales"),
        "shares": (["treasury_shares"], "shares_outstanding"),
        "ppe": (["depr"], "net_ppe"),
    },
)


def test_make_ledger_with_netting():
    chart = Chart(
        assets=["cash", "ppe"],
        expenses=[],
        equity=["shares"],
        liabilities=[],
        income=["sales"],
        contra_accounts={
            "sales": (["discounts", "returns"], "net_sales"),
            "shares": (["treasury_shares"], "shares_outstanding"),
            "ppe": (["depr"], "net_ppe"),
        },
    )
    ledger = make_ledger(chart)
    assert ledger == {
        "cash": Asset(debits=[], credits=[], netting=None),
        "ppe": Asset(
            debits=[],
            credits=[],
            netting=Netting(contra_accounts=["depr"], target_name="net_ppe"),
        ),
        "shares": Capital(
            debits=[],
            credits=[],
            netting=Netting(
                contra_accounts=["treasury_shares"], target_name="shares_outstanding"
            ),
        ),
        "sales": Income(
            debits=[],
            credits=[],
            netting=Netting(
                contra_accounts=["discounts", "returns"], target_name="net_sales"
            ),
        ),
        "discounts": ContraIncome(debits=[], credits=[]),
        "returns": ContraIncome(debits=[], credits=[]),
        "treasury_shares": ContraCapital(debits=[], credits=[]),
        "depr": ContraAsset(debits=[], credits=[]),
        "profit": IncomeSummaryAccount(debits=[], credits=[]),
    }
