"""Chart of accounts data structure."""

import itertools
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Tuple, Type

from pydantic import BaseModel  # type: ignore

from abacus.engine.accounts import (
    AssetName,
    CapitalName,
    ContraName,
    ExpenseName,
    IncomeName,
    IncomeSummaryAccount,
    LiabilityName,
    NullAccount,
    RegularAccount,
    RegularAccountEnum,
    RegularName,
    RetainedEarnings,
)
from abacus.engine.base import AbacusError, AccountName, Amount, Entry, Pair


def repeated_names(xs):
    return [k for k, v in Counter(xs).items() if v > 1]


def first(xs):
    return [x[0] for x in xs]


@dataclass
class ChartReviewer:
    chart: "Chart"


@dataclass
class ChartViewer:
    chart: "Chart"

    def contains(self, account_name: AccountName) -> bool:
        return account_name in self.account_names_all()

    def assert_contains(self, account_name: AccountName) -> None:
        if not self.contains(account_name):
            raise AbacusError(f"Account name <{account_name}> not in chart.")

    def get_regular_account_names(
        self, regular_account: RegularAccountEnum | Type[RegularAccount]
    ) -> List[AccountName]:
        if isinstance(regular_account, RegularAccountEnum):
            attribute = regular_account.value
        else:
            attribute = RegularAccountEnum.from_class(regular_account).value
        return getattr(self.chart, attribute)

    def get_contra_account_pairs(
        self, regular_account_type: RegularAccountEnum
    ) -> List[Tuple[AccountName, AccountName]]:
        """Get contra account pairs for all regular account types."""

        def get_one(regular_account_name):
            """Get all contra accounts for a given regular account."""
            r = regular_account_name
            try:
                return [
                    (r, contra_account_name)
                    for contra_account_name in self.chart.contra_accounts[r]
                ]
            except KeyError:
                return []

        return [
            pair
            for regular_account_name in self.get_regular_account_names(
                regular_account_type
            )
            for pair in get_one(regular_account_name)
        ]

    def account_names_regular(self) -> List[AccountName]:
        """Names of all regular accounts in chart."""
        return [
            account_name
            for regular_account in RegularAccountEnum.all()
            for account_name in self.get_regular_account_names(regular_account)
        ]

    def account_names_contra(self) -> List[AccountName]:
        """Names of contra accounts in chart."""
        return [v for values in self.chart.contra_accounts.values() for v in values]

    def account_names_unique(self) -> List[AccountName]:
        return first(self.yield_unique_accounts())

    def account_names_all(self) -> List[AccountName]:
        """Names of all regular accounts, contra accounts and unique accounts."""
        return (
            self.account_names_regular()
            + self.account_names_contra()
            + self.account_names_unique()
        )

    @property
    def duplicates(self):
        return repeated_names(self.account_names_all())

    def get_account_type(self, account_name: AccountName) -> Type:
        return dict(self.yield_all_accounts())[account_name]

    def yield_unique_accounts(self):
        yield self.chart.retained_earnings_account, RetainedEarnings
        yield self.chart.income_summary_account, IncomeSummaryAccount
        yield self.chart.null_account, NullAccount

    def yield_regular_accounts(self):
        for regular_account_type in RegularAccountEnum.all():
            cls = regular_account_type.cls()
            for account_name in self.get_regular_account_names(regular_account_type):
                yield account_name, cls

    def yield_contra_accounts(self):
        for regular_account_type in RegularAccountEnum.all():
            for account_name in self.get_regular_account_names(regular_account_type):
                if account_name in self.chart.contra_accounts.keys():
                    contra_cls = regular_account_type.contra_class()
                    for contra_account_name in self.chart.contra_accounts[account_name]:
                        yield contra_account_name, contra_cls
        yield from []

    def yield_all_accounts(self):
        return itertools.chain(
            self.yield_regular_accounts(),
            self.yield_contra_accounts(),
            self.yield_unique_accounts(),
        )


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

    def make_entries_for_operations(
        self, operation_names: List[str], amounts: List[str]
    ):
        return [
            Entry(*self.operations[on], Amount(amount))
            for on, amount in zip(operation_names, amounts)
        ]

    def add_operation(self, name: str, debit: AccountName, credit: AccountName):
        self.operations[name] = (debit, credit)
        return self

    def set_code(self, account_name: AccountName, code: str):
        self.codes[account_name] = code
        return self

    def set_name(self, account_name: AccountName, title: str):
        self.names[account_name] = title
        return self

    def validate(self):
        if dups := self.viewer.duplicates:
            raise AbacusError(f"The following account names were duplicated: {dups}")
        return self

    def offset(
        self,
        account_name: AccountName,
        contra_account_names: AccountName | List[AccountName],
    ):
        """Add contra accounts to chart."""
        if account_name not in self.viewer.account_names_regular():
            raise AbacusError(
                f"{account_name} must be specified in chart before adding contra accounts."
            )
        if not isinstance(contra_account_names, list):
            contra_account_names = [contra_account_names]
        try:
            self.contra_accounts[account_name].extend(contra_account_names)
        except KeyError:
            self.contra_accounts[account_name] = contra_account_names
        return self

    def ledger_dict(self):
        """Create ledger dictionary from chart. Used to create Ledger class."""
        return {
            account_name: cls()
            for account_name, cls in self.viewer.yield_all_accounts()
        }

    def ledger(self, starting_balances: Dict[AccountName, Amount] = {}):
        """Create ledger from chart."""
        from abacus.engine.ledger import Ledger, to_multiple_entry

        ledger = Ledger.new(self)
        entries = to_multiple_entry(ledger, starting_balances).entries(
            self.null_account
        )
        ledger.post_many(entries)
        return ledger

    @property
    def namer(self):
        return Namer(self)

    @property
    def viewer(self):
        return ChartViewer(self)


@dataclass
class Namer:
    """Get account names and titles."""

    chart: Chart

    def __getitem__(self, account_name: AccountName) -> str:
        try:
            return self.chart.names[account_name]
        except KeyError:
            return account_name.replace("_", " ").strip().capitalize()

    def compose_name(self, account_name: AccountName):
        """Produce name like 'cash (Cash)'."""
        return account_name + " (" + self[account_name] + ")"

    def compose_name_long(self, account_name: AccountName):
        """Produce name like 'asset:cash (Cash)'."""
        # t = self.chart.viewer.get_account_type(account_name).__name__
        n = self[account_name]
        return self.get_name(account_name).qualified() + " (" + n + ")"

    def get_name(self, account_name: AccountName) -> RegularName | ContraName:
        if account_name in self.chart.assets:
            return AssetName(account_name)
        elif account_name in self.chart.expenses:
            return ExpenseName(account_name)
        elif (
            account_name in self.chart.equity
            or account_name == self.chart.retained_earnings_account
        ):
            return CapitalName(account_name)
        elif account_name in self.chart.liabilities:
            return LiabilityName(account_name)
        elif account_name in self.chart.income:
            return IncomeName(account_name)
        for account, contra_acconts in self.chart.contra_accounts.items():
            if account_name in contra_acconts:
                return ContraName(account, account_name)
        raise AbacusError(f"Account name <{account_name}> not in chart.")
