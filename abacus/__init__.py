"""
A minimal, yet valid double-entry accounting system in Python that can do the following:

- define a chart of accounts and create a general ledger
- populate ledger with accounting entries
- close accounts properly at accounting period end
- produce trial balance, add adjustment entries
- produce income statement and balance sheet

Simplifying assumptions:

- one currency
- no journals, entries posted directly to ledger
- entry holds just amount, dr and cr accounts, no title or date
- no compound entries, entry affects exacly two accounts
- only balance sheet and income statement reports
- no non-negativity checks (can distribute dividend greater than profit)
- balances stick to one side (dr or cr) based on type of account

"""
from .accounting_types import AbacusError, Amount, Entry  # noqa: F401
from .book import Book  # noqa: F401
from .chart import Chart  # noqa: F401
from .ledger import Ledger  # noqa: F401
from .names import Names  # noqa: F401
from .reports import BalanceSheet, IncomeStatement  # noqa: F401
from .tables import PlainTextViewer, RichViewer  # noqa: F401
