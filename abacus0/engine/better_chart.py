from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple, Type

from pydantic import BaseModel

from abacus import AbacusError, Amount, Entry  # type: ignore
from abacus.engine.accounts import (  # type: ignore
    Asset,
    Capital,
    ContraAsset,
    ContraCapital,
    ContraExpense,
    ContraIncome,
    ContraLiability,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    NullAccount,
    RetainedEarnings,
    TAccount,
)
from abacus.engine.label_layer import (
    ContraLabel,
    Label,
    Prefix,
    RegularLabel,
    Unique,
    UniqueLabel,
    extract,
)


@dataclass
class Name:
    account_name: str
    contra_accounts: None | List[str]

    def _accounts(self, cls, contra_cls) -> Iterable[Tuple[str, Type[TAccount]]]:
        """Yield account name and class tuples.
        Used for creating ledger from chart."""
        yield self.account_name, cls
        if self.contra_accounts:
            for contra_account in self.contra_accounts:
                yield contra_account, contra_cls

    def accounts(self):
        pass


class AssetName(Name):
    def accounts(self):
        yield from self._accounts(Asset, ContraAsset)


class LiabilityName(Name):
    def accounts(self):
        yield from self._accounts(Liability, ContraLiability)


class CapitalName(Name):
    def accounts(self):
        yield from self._accounts(Capital, ContraCapital)


class IncomeName(Name):
    def accounts(self):
        yield from self._accounts(Income, ContraIncome)


class ExpenseName(Name):
    def accounts(self):
        yield from self._accounts(Expense, ContraExpense)


class RetainedEarningsName(Name):
    def accounts(self):
        yield self.account_name, RetainedEarnings


class IncomeSummaryName(Name):
    def accounts(self):
        yield self.account_name, IncomeSummaryAccount


class NullName(Name):
    def accounts(self):
        yield self.account_name, NullAccount


class BaseChart(BaseModel):
    """Chart of accounts."""

    assets: List[str] = []
    expenses: List[str] = []
    capital: List[str] = []
    liabilities: List[str] = []
    income: List[str] = []
    income_summary_account: str = ""  # = "current_profit"
    retained_earnings_account: str = ""  # "re"  # FIXME: change to retained_earnings
    null_account: str = ""  # = "null"
    contra_accounts: Dict[str, List[str]] = {}

    @property
    def check(self):
        return Check(self)

    def elevate(self):
        return Chart(base_chart=self)

    def append(self, attribute: str, account_name: str):
        """Append account name to given prefix attribute."""
        account_names = getattr(self, attribute)
        setattr(self, attribute, account_names + [account_name])

    def add_label(self, label: Label):
        match label:
            case RegularLabel(prefix, account_name):
                self.add_regular(prefix.attribute(), account_name)
            case ContraLabel(account_name, contra_account_name):
                self.add_contra(account_name, contra_account_name)
            case UniqueLabel(prefix, account_name):
                self.add_unique(prefix, account_name)

    def add_unique(self, prefix, account_name):
        self.check.does_not_exist(account_name)
        match prefix:
            case Unique.ISA:
                self.income_summary_account = account_name
            case Unique.RE:
                self.retained_earnings_account = account_name
            case Unique.NULL:
                self.null_account = account_name
        return self

    def add_regular(self, attribute: str, account_name: str):
        self.check.does_not_exist_in_attribute(account_name, attribute)
        self.check.does_not_exist(account_name)
        self.append(attribute, account_name)
        return self

    def add_contra(self, account_name, contra_account_name):
        self.check.exists(account_name).does_not_exist(contra_account_name)
        self.contra_accounts[account_name] = self.contra_accounts.get(
            account_name, []
        ) + [contra_account_name]
        return self

    def yield_names(self) -> Iterable[Name]:
        """Represent entire chart as stream of Name objects."""
        attributes = ["assets", "expenses", "capital", "liabilities", "income"]
        name_classes = [AssetName, ExpenseName, CapitalName, LiabilityName, IncomeName]
        for attribute, name_class in zip(attributes, name_classes):
            for account_name in getattr(self, attribute):
                contra_accounts = self.contra_accounts.get(account_name, [])
                yield name_class(account_name, contra_accounts)
        yield RetainedEarningsName(self.retained_earnings_account, None)
        yield IncomeSummaryName(self.income_summary_account, None)
        yield NullName(self.null_account, None)

    def yield_contra_account_pairs(
        self, name_class: Type[Name]
    ) -> Iterable[Tuple[str, str]]:
        """Used for closing accounts."""
        for name in self.yield_names():
            if isinstance(name, name_class):
                if name.contra_accounts is not None:
                    for contra_name in name.contra_accounts:
                        yield name.account_name, contra_name

    def yield_labels(self) -> Iterable[Tuple[str, Label]]:
        for prefix in list(Prefix):
            for account_name in getattr(self, prefix.attribute()):
                yield account_name, RegularLabel(prefix, account_name)
                for contra_name in self.contra_accounts.get(account_name, []):
                    yield contra_name, ContraLabel(account_name, contra_name)
        yield self.retained_earnings_account, UniqueLabel(
            Unique.RE, self.retained_earnings_account
        )
        yield self.income_summary_account, UniqueLabel(
            Unique.ISA, self.income_summary_account
        )
        yield self.null_account, UniqueLabel(Unique.NULL, self.null_account)

    def get_label(self, account_name: str) -> str:
        """Return 'asset:cash' for 'cash' and similar."""
        result = dict(self.yield_labels())
        return str(result[account_name])

    def ledger_items(self) -> Iterable[Tuple[str, Type[TAccount]]]:
        """Yield all account names and constructors for T-accounts."""
        for name in self.yield_names():
            for account_name, t_account_cls in name.accounts():
                yield account_name, t_account_cls

    def empty_ledger(self):
        """Create ledger object from chart."""
        from abacus.engine.ledger import Ledger

        return Ledger({name: t_account() for name, t_account in self.ledger_items()})

    def filter_accounts(self, account_classes: List[Type[TAccount]]) -> Iterable[str]:
        """Provide list of account names that are of given account classes.
        Used to find account names for closing contra accounts.
        """
        for account_name, account_cls in self.ledger_items():
            for account_class in account_classes:
                if account_cls == account_class:
                    yield account_name


class Chart(BaseModel):
    base_chart: BaseChart = BaseChart()
    titles: Dict[str, str] = {}
    operations: Dict[str, Tuple[str, str]] = {}

    def set_isa(self, account_name: str):
        """Change income summary account name."""
        self.base_chart.income_summary_account = account_name
        return self

    def set_null(self, account_name: str):
        """Change default name of null account."""
        self.base_chart.null_account = account_name
        return self

    def set_re(self, account_name: str):
        """Change default name of retained earnings account."""
        self.base_chart.retained_earnings_account = account_name
        return self

    def alias(self, operation: str, debit: str, credit: str):
        """Set alias for a pair of debit and credit accounts."""
        self.check.exists(debit).exists(credit)
        self.operations[operation] = (debit, credit)
        return self

    def offset(
        self, account_name: str, contra_account_name: str, title: str | None = None
    ):
        """Offset account with contra account."""
        return self.offset_many(account_name, contra_account_name, title)

    def offset_many(
        self,
        account_name: str,
        contra_account_names: str | List[str],
        title: str | None = None,
    ):
        """Offset account with one or many contra accounts."""
        if isinstance(contra_account_names, str):
            contra_account_names = [contra_account_names]
        if len(contra_account_names) == 1 and title:
            self.name(contra_account_names[0], title)
        for contra_account_name in contra_account_names:
            self.base_chart.add_contra(account_name, contra_account_name)
        return self

    @property
    def check(self):
        return Check(self.base_chart)

    @property
    def labels(self) -> Iterable[Label]:
        return [label for _, label in self.base_chart.yield_labels()]

    def name(self, account_name: str, title: str):
        """Set title for an account."""
        self.titles[account_name] = title
        return self

    def asset(self, account_name: str):
        """Add asset account to chart."""
        self.base_chart.add_regular("assets", account_name)
        return self

    def capital(self, account_name: str):
        """Add capital account to chart."""
        self.base_chart.add_regular("capital", account_name)
        return self

    def liability(self, account_name: str):
        """Add liability account to chart."""
        self.base_chart.add_regular("liabilities", account_name)
        return self

    def income(self, account_name: str):
        """Add income account to chart."""
        self.base_chart.add_regular("income", account_name)
        return self

    def expense(self, account_name: str):
        """Add expense account to chart."""
        self.base_chart.add_regular("expenses", account_name)
        return self

    def add(self, label_str: str, title: str | None = None):
        """Add account to chart by label like `asset:cash`."""
        match extract(label_str):
            case RegularLabel(prefix, account_name):
                self.base_chart.add_regular(prefix.attribute(), account_name)
                adding = account_name
            case ContraLabel(account_name, contra_account_name):
                self.base_chart.add_contra(account_name, contra_account_name)
                adding = contra_account_name
            case UniqueLabel(prefix, account_name):
                self.base_chart.add_unique(prefix, account_name)
                adding = account_name
        if title:
            self.name(adding, title)
        return self

    def get_title(self, account_name: str):
        """Produce name like 'Dividends due'."""
        default_name = account_name.replace("_", " ").strip().capitalize()
        return self.titles.get(account_name, default_name)

    def get_label(self, account_name: str):
        """Produce label like 'liability:dd'."""
        return self.base_chart.get_label(account_name)

    def print(self):
        print_chart(self)

    def make_entries_for_operations(
        self, operation_names: List[str], amounts: List[str]
    ):
        return [
            Entry(*self.operations[n], Amount(amount))
            for n, amount in zip(operation_names, amounts)
        ]

    def ledger(self, starting_balances: Dict[str, Amount] = {}):
        """Create ledger from chart."""
        from abacus.engine.ledger import to_multiple_entry

        ledger = self.base_chart.empty_ledger()
        me = to_multiple_entry(ledger, starting_balances)
        entries = me.entries(self.base_chart.null_account)
        ledger.post_many(entries)
        return ledger


@dataclass
class Check:
    chart: BaseChart

    def all_account_names(self):
        return [account_name for account_name, _ in self.chart.ledger_items()]

    def contains(self, account_name):
        return account_name in self.all_account_names()

    def exists(self, account_name):
        if not self.contains(account_name):
            raise AbacusError(
                f"Account name <{account_name}> must be specified in chart"
                " to enable this operation."
            )
        return self

    def does_not_exist(self, account_name):
        if self.contains(account_name):
            raise AbacusError(
                "Account name must be unique, "
                f"there is already <{account_name}> in chart."
            )
        return self

    def does_not_exist_in_attribute(self, account_name, attribute):
        if account_name in getattr(self.chart, attribute):
            raise AbacusError(
                f"Account name <{account_name}> already exists "
                f"within <{attribute}> chart attribute."
            )


def print_re(chart):
    print(
        "Retained earnings account:",
        chart.get_title(chart.base_chart.retained_earnings_account) + ".",
    )


def contra_phrase(account_name, contra_account_names):
    return account_name + " is offset by " + ", ".join(contra_account_names)


def print_chart(chart: Chart):
    def name(account_name):
        return chart.get_title(account_name)

    print("Accounts")
    for attribute in ("assets", "capital", "liabilities", "income", "expenses"):
        account_names = getattr(chart.base_chart, attribute)
        if account_names:
            print(attribute.capitalize() + ":", ", ".join(map(name, account_names)))
    if chart.base_chart.contra_accounts:
        print("Contra accounts:")
        for key, names in chart.base_chart.contra_accounts.items():
            print("  -", contra_phrase(name(key), map(name, names)))
    print_re(chart)
    if chart.operations:
        print("Operation aliases:")
        for key, (debit, credit) in chart.operations.items():
            print("  -", key, f"(debit is {debit}, credit is {credit})")


def default_chart(isa="current_profit", re="re", null="null") -> Chart:
    return Chart().set_isa(isa).set_re(re).set_null(null)
