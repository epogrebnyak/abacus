"""Closing accounts at period end"""

from typing import List, Type

from abacus.accounting_types import AccountName, Entry, Netting
from abacus.accounts import (Account, Asset, Capital, CreditAccount,
                             DebitAccount, Expense, Income,
                             IncomeSummaryAccount, Liability, RetainedEarnings)
from abacus.closing_types import (CloseContraAsset, CloseContraCapital,
                                  CloseContraExpense, CloseContraIncome,
                                  CloseContraLiability, CloseExpense,
                                  CloseIncome, CloseISA,
                                  get_closing_entry_type)
from abacus.ledger import Ledger

__all__ = ["closing_entries", "closing_entries_for_permanent_contra_accounts"]  # type: ignore


def subset(ledger: Ledger, netting: Netting, regular_cls: Type):
    """Yield link account and contra account name pairs."""
    for linked_account_name, contra_account_names in netting.items():
        linked_account = ledger[linked_account_name]
        if isinstance(linked_account, regular_cls):
            for contra_account_name in contra_account_names:
                yield linked_account_name, contra_account_name


def close_contra_accounts(
    ledger: Ledger, netting: Netting, regular_cls: Type
) -> List[CloseContraIncome | CloseContraExpense]:
    closing_entry_type = get_closing_entry_type(regular_cls)
    return [
        transfer_entry(
            account=ledger[contra_account_name],
            from_=contra_account_name,
            to_=linked_account_name,
        ).coerce(closing_entry_type)
        for linked_account_name, contra_account_name in subset(
            ledger, netting, regular_cls
        )
    ]


def transfer_entry(account: Account, from_: AccountName, to_: AccountName) -> Entry:
    amount = account.balance()
    if isinstance(account, DebitAccount):
        return Entry(dr=to_, cr=from_, amount=amount)
    elif isinstance(account, CreditAccount):
        return Entry(dr=from_, cr=to_, amount=amount)
    raise TypeError(account)


def closing_entries_for_permanent_contra_accounts(
    ledger: Ledger, netting: Netting
) -> List[CloseContraAsset | CloseContraCapital | CloseContraLiability]:
    def f(t: Type):
        return close_contra_accounts(ledger, netting, t)

    return f(Asset) + f(Capital) + f(Liability)


def close_to_isa(
    ledger: Ledger, cls: Type[Income | Expense]
) -> List[CloseIncome | CloseExpense]:
    isa = ledger.find_account_name(IncomeSummaryAccount)
    match cls.__name__:
        case "Income":
            _ledger = ledger.subset(Income)
            entry_cls = CloseIncome  # type: ignore
        case "Expense":
            _ledger = ledger.subset(Expense)
            entry_cls = CloseExpense  # type: ignore
        case _:
            raise TypeError(cls)
    return [
        transfer_entry(account, name, isa).coerce(entry_cls)
        for name, account in _ledger.items()
    ]


def closing_entry_isa_to_retained_earnings(
    ledger: "Ledger",
) -> CloseISA:
    isa = ledger.find_account_name(IncomeSummaryAccount)
    re = ledger.find_account_name(RetainedEarnings)
    return transfer_entry(ledger[isa], isa, re).coerce(CloseISA)


def closing_entries(ledger: Ledger, netting: Netting) -> List:  # List[ClosingEntry]
    """Return a list of closing entries that will:
    - close contra accounts related to income and expense;
    - close income and expense accounts to income summary account;
    - close income summary account to retained earnings.
    """
    # Close contra accounts associated with income and expense accounts
    es0 = close_contra_accounts(ledger, netting, Income)
    es1 = close_contra_accounts(ledger, netting, Expense)
    # We should run actual postings to get the proper state of
    # income and expense accoutns after closing of related contra accounts.
    # This operation can be optimised later, maybe we do not need to process
    # all ledger, just related parts of it.
    _dummy_ledger = ledger.process_postings(list(es0 + es1))
    # At this point we can issue IncomeStatement as income and expense accounts
    # do have netted values and ContrIncome and ContraExpense accounts have zero
    # balance.
    # Next.we aggregate profit or loss at income summary account
    es2 = close_to_isa(_dummy_ledger, Income)
    es3 = close_to_isa(_dummy_ledger, Expense)
    # We have to process these entries to get actual state of income summary account.
    # Again, we are ru-running whole ledger here - much room for optimisation!
    _dummy_ledger = _dummy_ledger.process_postings(list(es2 + es3))  # type: ignore
    # Move balance of income summary account to retained earnings
    es4 = closing_entry_isa_to_retained_earnings(_dummy_ledger)
    # return a list of closing entriesthat can be
    # saved or serilised and re-run on a ledger later.
    return es0 + es1 + es2 + es3 + [es4]
