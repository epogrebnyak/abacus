"""Ledger data structure, can be created from chart, used to post entries and produce reports."""
from collections import UserDict
from typing import Dict, List, Type, Tuple

from engine.accounts import CreditAccount, DebitAccount, TAccount
from engine.base import AccountName, Amount, Entry, MultipleEntry, AbacusError
from engine.chart import Chart, make_ledger_dict


class Ledger(UserDict[AccountName, TAccount]):
    """General ledger that holds all accounts. Accounts are referenced by name."""

    @classmethod
    def new(cls, chart: Chart) -> "Ledger":
        """Create an empty ledger from chart."""
        return Ledger(make_ledger_dict(chart))

    def apply(self, attribute: str):
        """Apply an *attribute* to all accounts in ledger and return a new ledger."""
        return Ledger(
            {
                account_name: getattr(taccount, attribute)()
                for account_name, taccount in self.items()
            }
        )

    def deep_copy(self) -> "Ledger":
        """Return a copy of the ledger, taking care of copying
        debit and credit lists in accounts."""
        return self.apply("deep_copy")

    def condense(self) -> "Ledger":
        """Purge data from ledger leaving only account balances.
        Creates a copy of ledger."""
        return self.apply("condense")

    def empty(self) -> "Ledger":
        """Purge data from ledger. Creates a copy of ledger."""
        return self.apply("empty")

    def balances(self) -> Dict[AccountName, Amount]:
        """Return account balances."""
        return dict(self.apply("balance").data)

    def subset(self, classes: Type | List[Type]) -> "Ledger":
        """Filter ledger by account type."""
        if not isinstance(classes, list):
            classes = [classes]

        def belongs(t_account: TAccount):
            return any(isinstance(t_account, cls) for cls in classes)

        return Ledger(
            [
                (account_name, t_account)
                for account_name, t_account in self.items()
                if belongs(t_account)
            ]
        )

    def post(self, entries: Entry | List[Entry]) -> "Ledger":
        # Note that post() mutates the existing data structure
        if isinstance(entries, list):
            post_entries(self, entries)
        elif isinstance(entries, Entry):
            post_entry(self, entries)
        else:
            raise TypeError(entries)
        return self

    def post_many(self, entries: List[Entry]) -> "Ledger":
        post_entries(self, entries)
        return self

    def close_some(self, chart: Chart) -> "Ledger":
        """Close contra accounts corresponding to income and expense.
        Returns a copy of a ledger.
        """
        from engine.closing import close_contra_expense as ce
        from engine.closing import close_contra_income as ci

        closing_entries = ci(chart, self) + ce(chart, self)
        return self.condense().post(closing_entries)

    def income_statement(self, chart: Chart, post_close_entries=None):
        from engine.report import IncomeStatement

        if post_close_entries is None:
            post_close_entries = []
        ledger = self.condense().close_some(chart).post_many(post_close_entries)
        return IncomeStatement.new(ledger)

    def close(self, chart: Chart) -> "Ledger":
        """Close all accounts related to retained earnings and to permanent accounts.
        Returns a copy of a ledger.
        """
        from engine.closing import flush_permanent_accounts, make_closing_entries

        closing_entries = make_closing_entries(
            chart, self
        ).all() + flush_permanent_accounts(chart, self)
        return self.condense().post_many(closing_entries)

    def balance_sheet(self, chart: Chart, post_close_entries=None):
        from engine.report import BalanceSheet

        if post_close_entries is None:
            post_close_entries = []
        ledger = self.close(chart).post_many(post_close_entries)
        return BalanceSheet.new(ledger)

    def trial_balance(self, chart: Chart):
        from engine.report import view_trial_balance

        return view_trial_balance(chart, self)


def post_entry(ledger: Ledger, entry: Entry) -> None:
    ledger[entry.debit].debit(entry.amount)
    ledger[entry.credit].credit(entry.amount)


def post_entries(ledger: Ledger, entries: List[Entry]):
    ledger, failed_entries = unsafe_post_entries(ledger, entries)
    if failed_entries:
        raise AbacusError(failed_entries)


def unsafe_post_entries(
    ledger: Ledger, entries: List[Entry]
) -> Tuple[Ledger, List[Entry]]:
    failed = []
    for entry in entries:
        try:
            post_entry(ledger, entry)
        except KeyError:
            failed.append(entry)
    return ledger, failed


def to_multiple_entry(ledger: Ledger, starting_balances: dict) -> MultipleEntry:
    debit_entries = []
    credit_entries = []
    for account_name in starting_balances.keys():
        try:
            ledger[account_name]
        except KeyError:
            raise AbacusError(f"Account {account_name} does not exist in ledger.")
    for account_name, amount in starting_balances.items():
        match ledger[account_name]:
            case DebitAccount(_, _):
                debit_entries.append((account_name, amount))
            case CreditAccount(_, _):
                credit_entries.append((account_name, amount))
    return MultipleEntry(debit_entries, credit_entries).validate()
