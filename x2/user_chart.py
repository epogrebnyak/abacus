from dataclasses import dataclass, field
from typing import Iterable

from core import AbacusError, Account, Chart, T
from pathlib import Path


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


@dataclass
class Composer:
    contra: str = "contra"
    translation: dict[str, str] = field(default_factory=dict)

    def add(self, t: T, alt_prefix: str):
        self.translation[alt_prefix] = t.value
        return self

    def select(self, incoming_prefix: str):
        return T(self.translation.get(incoming_prefix, incoming_prefix))

    def extract(self, input_string: str):
        return list(extract(input_string, self))


def extract(
    input_string: str, composer: Composer | None = None
) -> Iterable[Label] | Iterable[Offset]:
    """Extract one or several account labels from an input string.

    Input string examples:

    - "asset:cash"
    - "asset:cash,ap,inventory"
    - "income:sales"
    - "contra:sales:refunds"
    - "contra:sales:refunds,voids"

    """
    if composer is None:
        composer = Composer()
    match input_string.split(":"):
        case [prefix, name]:
            t = composer.select(prefix)
            for name_part in name.split(","):
                yield Label(t, name_part)
        case [composer.contra, name, contra_name]:
            for contra_name_part in contra_name.split(","):
                yield Offset(name, contra_name_part)
        case _:
            raise AbacusError(f"Cannot parse label string: {input_string}.")


from pydantic import BaseModel


class UserChart(BaseModel):
    income_summary_account: str
    retained_earnings_account: str
    null_account: str
    account_labels: dict[str, AccountLabel] = {}

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
                try:
                    self.account_labels[name].offset(contra_name)
                except KeyError:
                    raise AbacusError(
                        f"Cannot offset {name} because it is not in chart."
                    )

    def use(self, *label_strings: str, composer: Composer | None = None):
        if composer is None:
            composer = Composer()
        for label_string in label_strings:
            for obj in extract(label_string, composer):
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

    def save(self, path: Path | str):
        Path(path).write_text(self.json(indent=4, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path | str):
        return cls.parse_file(path)


def user_chart(*args):
    return UserChart(
        income_summary_account="isa",
        retained_earnings_account="re",
        null_account="null",
    ).use(*args)
