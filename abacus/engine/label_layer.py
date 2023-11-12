from dataclasses import dataclass
from enum import Enum
from typing import List

from abacus import AbacusError


class Prefix(Enum):
    ASSET = "asset"
    CAPITAL = "capital"
    LIABILITY = "liability"
    INCOME = "income"
    EXPENSE = "expense"

    def attribute(self):
        return to_attribute(self)


def to_attribute(prefix: Prefix) -> str:
    """Return BaseChart class attribute name for given prefix."""
    p = prefix.value
    try:
        return dict(asset="assets", liability="liabilities", expense="expenses")[p]
    except KeyError:
        return p


class Label:
    pass


@dataclass
class RegularLabel(Label):
    """Label for regular accounts."""

    prefix: Prefix
    account_name: str

    def __str__(self):
        return f"{self.prefix.value}:{self.account_name}"


class Unique(Enum):
    RE = "re"
    ISA = "isa"
    NULL = "null"


@dataclass
class UniqueLabel(Label):
    """Label for unique accounts."""

    prefix: Unique
    account_name: str

    def __str__(self):
        return f"{self.prefix.value}:{self.account_name}"


@dataclass
class ContraLabel(Label):
    """Label for contra accounts."""

    account_name: str
    contra_account_name: str

    def __str__(self):
        return f"contra:{self.account_name}:{self.contra_account_name}"


def extract(label_str: str) -> Label:
    match label_str.lower().split(":"):
        case Unique.RE.value, account_name:
            return UniqueLabel(Unique.RE, account_name)
        case Unique.NULL.value, account_name:
            return UniqueLabel(Unique.NULL, account_name)
        case Unique.ISA.value, account_name:
            return UniqueLabel(Unique.ISA, account_name)
        case (prefix_str, account_name):
            return RegularLabel(detect_prefix(prefix_str), account_name)
        case "contra", account_name, contra_account_name:
            return ContraLabel(account_name, contra_account_name)
        case _:
            raise AbacusError(f"Invalid account label: {label_str}")


def mapping():
    return [
        (Prefix.ASSET, ["asset", "assets"]),
        (Prefix.CAPITAL, ["capital", "equity"]),
        (Prefix.LIABILITY, ["liability", "liabilities"]),
        (Prefix.INCOME, ["income"]),
        (Prefix.EXPENSE, ["expense", "expenses"]),
    ]


def detect_prefix(prefix_str: str) -> Prefix:
    return {x: prefix for prefix, xs in mapping() for x in xs}[prefix_str.lower()]


def to_chart(labels: List[str]):
    """Return a BaseChart instance from a list of account labels."""
    from abacus.engine.better_chart import BaseChart

    base_chart = BaseChart()
    for label in labels:
        print(label)
        print(extract(label))
        base_chart.add_label(extract(label))
    return base_chart
