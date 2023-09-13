"""Chart of accounts data structure."""

from collections import Counter
from typing import Dict, List, Type

from engine.accounts import (
    IncomeSummaryAccount,
    NullAccount,
    RegularAccount,
    RetainedEarnings,
    mapping,
)
from engine.base import AbacusError, AccountName, Amount, Pair
from pydantic import BaseModel  # type: ignore


def repeated_names(xs):
    return [k for k, v in Counter(xs).items() if v > 1]


class Chart(BaseModel):
    """Chart of accounts."""

    assets: List[AccountName] = []
    expenses: List[AccountName] = []
    equity: List[AccountName] = []
    liabilities: List[AccountName] = []
    income: List[AccountName] = []
    retained_earnings_account: AccountName = "re"
    income_summary_account: AccountName = "current_profit"
    null_account = (
        "null"  # corresponding account to add starting balances using signle entries
    )
    contra_accounts: Dict[AccountName, List[AccountName]] = {}
    names: Dict[AccountName, str] = {"re": "Retained earnings"}
    codes: Dict[AccountName, str] = {}
    operations: Dict[str, Pair] = {}

    def five_types_of_accounts(self):
        return ("assets", "equity", "liabilities", "income", "expenses")

    def add_operation(self, name: str, debit: AccountName, credit: AccountName):
        self.operations[name] = (debit, credit)
        return self

    def set_code(self, account_name: AccountName, code: str):
        self.codes[account_name] = code
        return self

    def set_name(self, account_name: AccountName, title: str):
        self.names[account_name] = title
        return self

    def get_name(self, account_name: AccountName) -> str:
        try:
            return self.names[account_name]
        except KeyError:
            return account_name.replace("_", " ").strip().capitalize()

    def compose_name(self, account_name: AccountName):
        """Produce name like 'cash (Cash)'."""
        return account_name + " (" + self.get_name(account_name) + ")"

    def compose_name_long(self, account_name: AccountName):
        """Produce name like 'asset:cash (Cash)'."""
        t = self.get_account_type(account_name).__name__
        n = self.get_name(account_name)
        return t + ":" + account_name + " (" + n + ")"

    @property
    def duplicates(self):
        return repeated_names(self.account_names_all())

    def validate(self):
        if self.duplicates:
            raise AbacusError(
                f"Following account names were duplicated: {self.duplicates}"
            )
        return self

    def offset(
        self,
        account_name: AccountName,
        contra_account_names: AccountName | List[AccountName],
    ):
        """Add contra accounts to chart."""
        if account_name not in self.account_names_all():
            raise AbacusError(
                f"{account_name} must be specified in chart before adding {contra_account_names}."
            )
        if not isinstance(contra_account_names, list):
            contra_account_names = [contra_account_names]
        try:
            self.contra_accounts[account_name].extend(contra_account_names)
        except KeyError:
            self.contra_accounts[account_name] = contra_account_names
        return self

    def account_names_regular(self) -> List[AccountName]:
        return [
            account_name
            for attribute, _ in mapping()
            for account_name in getattr(self, attribute)
        ]

    def account_names_contra(self) -> List[AccountName]:
        return [v for values in self.contra_accounts.values() for v in values]

    def account_names_all(self) -> List[AccountName]:
        """Names of all regular accounts, contra accounts and unique accounts."""
        return (
            self.account_names_regular()
            + self.account_names_contra()
            + [
                self.retained_earnings_account,
                self.income_summary_account,
                self.null_account,
            ]
        )

    def account_names(self, cls: Type[RegularAccount]) -> List[AccountName]:
        """Return account names for account class *cls*."""
        reverse_dict = {
            Class.__name__: attribute for attribute, (Class, _) in mapping()
        }
        attribute = reverse_dict[cls.__name__]  # "assets" for example
        return getattr(self, attribute)

    def contra_account_pairs(self, cls: Type[RegularAccount]):
        """Yield pairs of regular and contra account names for given regular account type *cls*.
        This action unpacks self.conta_accounts to a sequence of tuples, each tuple is
        a pair of account names."""
        for regular_account_name, contra_account_names in self.contra_accounts.items():
            if regular_account_name in self.account_names(cls):
                for contra_account_name in contra_account_names:
                    yield regular_account_name, contra_account_name

    def get_account_type(self, account_name: AccountName) -> Type:
        return dict(yield_all_accounts(self))[account_name]

    def ledger(self, starting_balances: Dict[AccountName, Amount] = {}):
        """Create ledger from chart."""
        from engine.ledger import Ledger, to_multiple_entry

        ledger = Ledger.new(self)
        entries = to_multiple_entry(ledger, starting_balances).entries(
            self.null_account
        )
        ledger.post_many(entries)
        if (x := ledger[self.null_account].balance()) != 0:
            raise AbacusError(
                f"Balance of null account after adding starting balances must be 0, got {x}."
            )
        return ledger


def yield_all_accounts(chart: Chart):
    for attribute, (Class, ContraClass) in mapping():
        for account_name in getattr(chart, attribute):
            # regular accounts
            yield account_name, Class
            try:
                # contra accounts if found
                for contra_account_name in chart.contra_accounts[account_name]:
                    yield contra_account_name, ContraClass
            except KeyError:
                pass
    yield chart.retained_earnings_account, RetainedEarnings
    yield chart.income_summary_account, IncomeSummaryAccount
    yield chart.null_account, NullAccount


def make_ledger_dict(chart: Chart) -> Dict:
    """Create ledger dictionary from chart. Used to create Ledger class."""
    ledger = {}
    for account_name, cls in yield_all_accounts(chart):
        ledger[account_name] = cls()
    return ledger
