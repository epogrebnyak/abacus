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
from engine.base import AbacusError, AccountName
from pydantic import BaseModel  # pylint: disable=import-error # type: ignore


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
        "null"  # corresponding account to add starting balances with signle entries
    )
    contra_accounts: Dict[AccountName, List[AccountName]] = {}
    names: Dict[AccountName, str] = {}

    def set_name(self, account_name: AccountName, title: str):
        self.names[account_name] = title
        return self

    def get_name(self, account_name: AccountName) -> str:
        try:
            return self.names[account_name]
        except KeyError:
            return account_name.replace("_", " ").strip().capitalize()

    @property
    def duplicates(self):
        return repeated_names(self.account_names_all())

    def validate(self) -> True:
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
        if account_name not in self.all_account_names():
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

    def account_names_all(self) -> List[AccountName]:
        """Names of all regular accounts, contra accounts and unique accounts."""
        return (
            [
                account_name
                for attribute, _ in mapping()
                for account_name in getattr(self, attribute)
            ]
            + [v for values in self.contra_accounts.values() for v in values]
            + [
                self.retained_earnings_account,
                self.income_summary_account,
                self.null_account,
            ]
        )

    def account_names(self, cls: Type[RegularAccount]) -> List[AccountName]:
        """Return account name list for account class *cls* or return all accounts."""
        reverse_dict = {
            Class.__name__: attribute for attribute, (Class, _) in mapping()
        }
        return getattr(self, reverse_dict[cls.__name__])

    def contra_account_pairs(self, cls: Type[RegularAccount]):
        """Yield pairs of regular and contra account names for given account type *cls*.
        This action unpacks self.conta_accounts to a sequence of tuples, each tuple is
        a pair of account names."""
        for regular_account_name, contra_account_names in self.contra_accounts.items():
            if regular_account_name in self.account_names(cls):
                for contra_account_name in contra_account_names:
                    yield regular_account_name, contra_account_name


def make_ledger_dict(chart: Chart) -> Dict:
    """Create ledger dictionary from chart. Used to create Ledger class."""
    ledger = {}
    for attribute, (Class, ContraClass) in mapping():
        for account_name in getattr(chart, attribute):
            # create regular accounts
            ledger[account_name] = Class()
            try:
                # create contra accounts if found
                for contra_account_name in chart.contra_accounts[account_name]:
                    ledger[contra_account_name] = ContraClass()
            except KeyError:
                pass
    ledger[chart.retained_earnings_account] = RetainedEarnings()
    ledger[chart.income_summary_account] = IncomeSummaryAccount()
    ledger[chart.null_account] = NullAccount()
    return ledger
