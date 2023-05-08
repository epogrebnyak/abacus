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
    DebitAccount,
    CreditAccount,
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


def make_ledger2(chart):
    account_types = chart.account_types()
    ledger = make_regular_accounts(chart)
    for nets_with, (contra_accounts, target_account) in chart.contra_accounts.items():
        for contra_account_name in contra_accounts:
            match account_types[nets_with]():
                case DebitAccount():
                    ledger[contra_account_name] = CreditContraAccount()
                    ledger[nets_with].netting = Netting(contra_accounts, target_account)
                case CreditAccount():
                    ledger[contra_account_name] = DebitContraAccount()
                    ledger[nets_with].netting = Netting(contra_accounts, target_account)
                case _:
                    raise TypeError
    ledger[chart.income_summary_account] = IncomeSummaryAccount()
    return ledger


def make_regular_accounts(chart):
    ledger = Ledger()
    regular_attributes = ["assets", "expenses", "equity", "liabilities", "income"]
    account_types = chart.account_types()
    for attr in regular_attributes:
        for account_name in getattr(chart, attr):
            ledger[account_name] = account_types[account_name]()
    return ledger


print(make_ledger2(chart))


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
    ledger = make_ledger2(chart)
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
    """Account name and balance.

    Note: 'saldo' in balance in Italian."""

    account_name: AccountName
    amount: Amount


# Next:
# close_contra_accounts(ledger, cls) - closes all contraccounts related to cls
# close_income(ledger) nets income-related contraccounts
# close_expense(ledger) nets expense-related contraccounts (maybe there are none)
# close_isa(ledger, retained_earnings_account_name) moves income and expense to isa
# and closes isa to retained earnings (this keeps track of entries in isa)
# income statement (net values) produced here
# close all other contra_accounts (depreciation)
