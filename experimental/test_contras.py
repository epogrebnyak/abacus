# %%
from dataclasses import dataclass
from typing import Dict, List, Optional

from abacus import Chart
from abacus.accounting_types import (
    Account,
    AccountBalancesDict,
    AccountName,
    Amount,
    Asset,
    BalanceSheet,
    Capital,
    Chart,
    CreditContraAccount,
    DebitContraAccount,
    Entry,
    Expense,
    Income,
    IncomeStatement,
    IncomeSummaryAccount,
    Ledger,
    Liability,
    Netting,
)
from abacus.core import AccountName, Amount


def test_make_ledger_with_netting():
    chart = Chart(
        assets=["cash", "ppe"],
        expenses=[],
        equity=["shares"],
        liabilities=[],
        income=["sales"],
        debit_contra_accounts=[
            ("discounts", "sales"),
            ("returns", "sales"),
            ("treasury_shares", "shares"),
        ],
        credit_contra_accounts=[("depr", "ppe")],
    )
    ledger = chart.make_ledger()
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
                contra_accounts=["treasury_shares"], target_name="net_shares"
            ),
        ),
        "sales": Income(
            debits=[],
            credits=[],
            netting=Netting(
                contra_accounts=["discounts", "returns"], target_name="net_sales"
            ),
        ),
        "discounts": DebitContraAccount(debits=[], credits=[]),
        "returns": DebitContraAccount(debits=[], credits=[]),
        "treasury_shares": DebitContraAccount(debits=[], credits=[]),
        "depr": CreditContraAccount(debits=[], credits=[]),
        "profit": IncomeSummaryAccount(debits=[], credits=[]),
    }


def test_invalid_contra_account_name_not_found():
    import pytest

    with pytest.raises(ValueError):
        Chart(
            assets=["ppe"],
            expenses=[],
            equity=[],
            liabilities=[],
            income=["sales"],
            debit_contra_accounts=[],
            credit_contra_accounts=[("abc", "zzz")],
        )


def test_invalid_contra_account_wrong_side():
    import pytest

    with pytest.raises(ValueError):
        Chart(
            assets=["ppe"],
            expenses=[],
            equity=[],
            liabilities=[],
            income=["sales"],
            debit_contra_accounts=[("depr", "ppe")],  # should be credit_contra_accounts
            credit_contra_accounts=[],
        )


@dataclass
class Saldo:
    """Account name and balance (in Italian and some other languages)."""

    account_name: AccountName
    amount: Amount
