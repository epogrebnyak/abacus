"""Closing accounts at period end"""

from typing import List

from abacus.accounting_types import Entry
from abacus.accounts import (
    Asset,
    Capital,
    CreditAccount,
    DebitAccount,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    RetainedEarnings,
)
from abacus.closing_types import (
    CloseExpense,
    CloseIncome,
    CloseISA,
    get_closing_entry_type,
)
from abacus.ledger import expenses, income
from abacus.ledger import Ledger

__all__ = ["closing_entries", "closing_entries_for_permanent_contra_accounts"]  # type: ignore


def close_contra_accounts(ledger, netting, regular_cls):
    res = []
    for linked_account, contra_accounts in netting.items():
        if isinstance(ledger[linked_account], regular_cls):
            closing_entry_type = get_closing_entry_type(regular_cls)
            for contra_account in contra_accounts:
                entry = transfer_entry(
                    ledger[contra_account], contra_account, linked_account
                )
                res.append(entry.coerce(closing_entry_type))
    return res


def transfer_entry(account, from_, to_):
    amount = account.balance()
    if isinstance(account, DebitAccount):
        return Entry(dr=to_, cr=from_, amount=amount)
    elif isinstance(account, CreditAccount):
        return Entry(dr=from_, cr=to_, amount=amount)
    raise TypeError(account)


def closing_entries_for_permanent_contra_accounts(ledger, netting) -> List:
    def f(t):
        return close_contra_accounts(ledger, netting, t)

    return f(Asset) + f(Capital) + f(Liability)

def close_to_isa(ledger, cls) -> List[CloseIncome | CloseExpense]:

    isa = ledger.find_account_name(IncomeSummaryAccount)
    match cls.__name__:
        case "Income":
           select = income
           entry_cls = CloseIncome # type: ignore
        case "Expense":
           select = expenses
           entry_cls = CloseExpense # type: ignore
        case _:
            raise TypeError(cls)   
    return [
        transfer_entry(account, name, isa).coerce(entry_cls)
        for name, account in select(ledger).items()
    ]


def closing_entry_isa_to_retained_earnings(
    ledger: "Ledger",
) -> CloseISA:
    isa = ledger.find_account_name(IncomeSummaryAccount)
    re = ledger.find_account_name(RetainedEarnings)
    return transfer_entry(ledger[isa], isa, re).coerce(CloseISA)


def closing_entries(ledger: Ledger, netting) -> List:
    # Close contra accounts associated with income and expense accounts
    es0 = close_contra_accounts(ledger, netting, Income)
    es1 = close_contra_accounts(ledger, netting, Expense)
    _dummy_ledger = ledger.process_postings(es0 + es1)
    # At this point we can issue IncomeStatement
    # Next. aggregate profit or loss at income summary account
    es2 = close_to_isa(_dummy_ledger, Income)
    es3 = close_to_isa(_dummy_ledger, Expense)
    _dummy_ledger = _dummy_ledger.process_postings(es2 + es3)  # type: ignore
    # Move balance of income summary account to retained earnings
    es4 = closing_entry_isa_to_retained_earnings(_dummy_ledger)
    return es0 + es1 + es2 + es3 + [es4]
