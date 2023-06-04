"""Journal of entries and general ledger."""

from collections import UserDict, UserList
from typing import List, Tuple

from abacus.accounts import Account, Asset, Capital, Expense, Income, Liability

from .accounting_types import (
    AbacusError,
    AccountName,
    Amount,
    BaseEntry,
    BusinessEntry,
    CloseExpense,
    CloseIncome,
    Entry,
    OpenContraAccount,
    OpenRegularAccount,
    Posting,
)


def yield_until(xs, classes):
    for x in xs:
        if any(isinstance(x, cls) for cls in classes):
            break
        yield x


class Journal(UserList[Posting]):
    """General ledger that holds all accounts."""

    @classmethod
    def from_file(cls, path):
        return cls()

    def post_entries(self, entries: List[Posting]) -> "Journal":
        self.data.extend(entries)
        return self

    def open_account(self, name, type, balance, link=None):
        if link:
            p = OpenContraAccount(name, type.__name__, balance, link)
        else:
            p = OpenRegularAccount(name, type.__name__, balance)
        self.data.append(p)
        return self

    def post(self, dr: AccountName, cr: AccountName, amount: Amount) -> "Journal":
        entry = BusinessEntry(dr, cr, amount)
        return self.post_entries([entry])

    def adjust(self, dr, cr, amount) -> "Journal":
        raise NotImplementedError

    def postclose(self, dr, cr, amount) -> "Journal":
        raise NotImplementedError

    def close(self) -> "Journal":
        from abacus.closing import closing_entries

        self.post_entries(closing_entries(self.ledger()))  # type: ignore
        return self

    def current_profit(self):
        return self.income_statement().current_profit()

    def ledger(self):
        return Ledger().process_entries(self.data)

    def balances(self):
        from .reports import balances

        return balances(self.ledger())

    def balance_sheet(self):
        from .reports import balance_sheet

        return balance_sheet(self.ledger())

    def income_statement(self):
        from .reports import IncomeStatement, balances

        _gen = yield_until(self.data, [CloseExpense, CloseIncome])
        _ledger = Ledger().process_entries(_gen)
        return IncomeStatement(
            income=balances(income(_ledger)),
            expenses=balances(expenses(_ledger)),
        )


class Ledger(UserDict[AccountName, Account]):
    """General ledger that holds all accounts."""

    def safe_copy(self) -> "Ledger":
        return Ledger((k, account.safe_copy()) for k, account in self.items())

    def process_entries(self, entries) -> "Ledger":
        return process_postings(self, entries)

    def process_entry(self, dr, cr, amount) -> "Ledger":
        return process_postings(self, [Entry(dr, cr, amount)])

    def close(self) -> "Ledger":
        """Close contraaccounts associated with income and expense accounts,
        aggregate profit or loss at income summary account
        and move balance of income summary account to retained earnings."""
        from .closing import close

        return close(self)

    def balances(self):
        from .reports import balances

        return balances(self)

    def balance_sheet(self):
        from .reports import balance_sheet

        return balance_sheet(self)

    def is_closed(self) -> bool:
        # - income and expense contra accounts are zero
        # - income and expense accounts are zero
        # - isa is zero
        raise NotImplementedError


def subset_by_class(ledger, cls):
    return Ledger(
        (account_name, account)
        for account_name, account in ledger.items()
        if isinstance(account, cls)
    )


def assets(ledger: Ledger) -> Ledger:
    return subset_by_class(ledger, Asset)


def expenses(ledger: Ledger) -> Ledger:
    return subset_by_class(ledger, Expense)


def capital(ledger: Ledger) -> Ledger:
    return subset_by_class(ledger, Capital)


def liabilities(ledger: Ledger) -> Ledger:
    return subset_by_class(ledger, Liability)


def income(ledger: Ledger) -> Ledger:
    return subset_by_class(ledger, Income)


def process_postings(ledger: Ledger, postings: List[Posting]) -> Ledger:
    ledger, _failed_entries = safe_process_postings(ledger, postings)
    if _failed_entries:
        raise AbacusError(_failed_entries)
    return ledger


def check_not_exists(ledger, account_name):
    if account_name in ledger.keys():
        raise AbacusError("Cannot open: account {account_name} already exists.")


def _process(ledger: Ledger, posting: Posting) -> Ledger:
    from abacus.accounts import get_class_constructor

    match posting:
        case OpenContraAccount(account_name, cls_string, amount, link):
            check_not_exists(ledger, account_name)
            cls = get_class_constructor(cls_string)
            ledger[account_name] = cls([], [], link).start(amount)
        case OpenRegularAccount(account_name, cls_string, amount):
            check_not_exists(ledger, account_name)
            cls = get_class_constructor(cls_string)
            ledger[account_name] = cls([], []).start(amount)
        case Entry(dr, cr, amount):
            ledger[dr].debits.append(amount)
            ledger[cr].credits.append(amount)
        case BaseEntry(dr, cr, amount, _):
            ledger[dr].debits.append(amount)
            ledger[cr].credits.append(amount)
    return ledger


def safe_process_postings(
    ledger: Ledger, postings: List[Posting]
) -> Tuple[Ledger, List[Posting]]:
    _ledger = ledger.safe_copy()
    _failed = []
    for posting in postings:
        try:
            _ledger = _process(_ledger, posting)
        except KeyError:
            _failed.append(posting)
    return _ledger, _failed
