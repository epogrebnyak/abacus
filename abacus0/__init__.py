"""
A minimal, yet valid double-entry accounting system in Python that can:

- define a chart of accounts and create a ledger,
- post entries to ledger,
- produce trial balance,
- post adjustment entries,
- close accounts at accounting period end,
- produce income statement and balance sheet,
- make post-close entries.

Simplifying assumptions:

- one currency
- no journals, entries posted directly to ledger
- entry holds just amount, debit and credit accounts, no title or date
- only balance sheet and income statement reports, no cash flow or changes in equity
- no non-negativity checks (eg can distribute dividend greater than profit)
- balances stick to one side only (debit or credit) based on specified type of account

"""
from .engine.base import AbacusError, Amount, Entry, MultipleEntry  # noqa: F401
from .engine.better_chart import BaseChart, Chart  # noqa: F401
from .engine.entries import LineJSON  # noqa: F401
from .engine.ledger import Ledger  # noqa: F401
from .engine.report import BalanceSheet, IncomeStatement  # noqa: F401
