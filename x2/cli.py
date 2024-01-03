from fine import T, AbacusError, Chart, Account, T
from typing import Iterable
from dataclasses import dataclass, field


@dataclass
class AccountLabel:
    t: T
    contra_names: list[str] = field(default_factory=list)

    def offset(self, name):
        self.contra_names.append(name)
        return self


@dataclass
class Label:
    t: T
    name: str


@dataclass
class Offset:
    name: str
    contra_name: str


def extract(
    label_string: str, contra_prefix: str = "contra"
) -> Iterable[Label] | Iterable[Offset]:
    match label_string.split(":"):
        case [prefix, name]:
            for name_part in name.split(","):
                yield Label(T(prefix), name_part)
        case [contra_prefix, name, contra_name]:
            for contra_name_part in contra_name.split(","):
                yield Offset(name, contra_name_part)
        case _:
            raise AbacusError(f"Cannot parse label string: {label_string}.")


@dataclass
class UserChart:
    income_summary_account: str
    retained_earnings_account: str
    null_account: str
    account_labels: dict[str, AccountLabel] = field(default_factory=dict)

    def yield_names(self):
        yield self.income_summary_account
        yield self.retained_earnings_account
        yield self.null_account
        yield from self.account_labels.keys()
        for label in self.account_labels.values():
            for contra_name in label.contra_names:
                yield contra_name

    @property
    def names(self):
        return list(self.yield_names())

    def assert_unique(self, name):
        if name in self.names:
            raise AbacusError(f"Duplicate account name: {name}")

    def add_one(self, obj: Label | Offset):
        match obj:
            case Label(t, name):
                self.assert_unique(name)
                self.account_labels[name] = AccountLabel(t, [])
            case Offset(name, contra_name):
                self.assert_unique(contra_name)
                self.account_labels[name].offset(contra_name)

    def use(self, *label_strings: str):
        for label_string in label_strings:
            for obj in extract(label_string):
                self.add_one(obj)
        return self

    def set_isa(self, name):
        self.income_summary_account = self.assert_unique(name)

    def set_re(self, name):
        self.retained_earnings_account = self.assert_unique(name)

    def set_null(self, name):
        self.null_account = self.assert_unique(name)

    def accounts(self, t: T):
        return [
            Account(name, label.contra_names)
            for name, label in self.account_labels.items()
            if label.t == t
        ]

    def chart(self):
        return Chart(
            income_summary_account=self.income_summary_account,
            retained_earnings_account=self.retained_earnings_account,
            null_account=self.null_account,
            assets=self.accounts(T.Asset),
            capital=self.accounts(T.Capital),
            liabilities=self.accounts(T.Liability),
            income=self.accounts(T.Income),
            expenses=self.accounts(T.Expense),
        ).validate()


def make_chart(label_string_long: str):
    return UserChart("isa", "re", "null").use(*label_string_long.split())
