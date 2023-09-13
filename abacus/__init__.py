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
- only balance sheet and income statement reports, no cash flow
- no non-negativity checks (can distribute dividend greater than profit)
- balances stick to one side (debit or credit) based on type of account

"""
from .engine.base import AbacusError, Amount, Entry  # noqa: F401
from .engine.chart import Chart  # noqa: F401
from .engine.ledger import Ledger  # noqa: F401
from .engine.report import BalanceSheet, IncomeStatement  # noqa: F401
