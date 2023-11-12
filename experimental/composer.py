from dataclasses import dataclass, field
from itertools import chain, groupby
from typing import Iterable, Type

from pydantic import BaseModel

import abacus.engine.accounts as accounts
from abacus import Ledger


@dataclass
class Title:
    name: str
    title: str


@dataclass
class Offset:
    name: str
    contra: str


@dataclass
class Alias:
    operation: str
    debit: str
    credit: str


@dataclass
class Label:
    name: str


class AssetLabel(Label):
    pass


class LiabilityLabel(Label):
    pass


class ExpenseLabel(Label):
    pass


class IncomeLabel(Label):
    pass


class CapitalLabel(Label):
    pass


class RetainedEarningsLabel(Label):
    pass


class IncomeSummaryLabel(Label):
    pass


class NullLabel(Label):
    pass


@dataclass
class Composer:
    asset: str = "asset"
    capital: str = "capital"
    liability: str = "liability"
    income: str = "income"
    expense: str = "expense"
    contra: str = "contra"
    income_summary: str = "isa"
    retained_earnings: str = "re"
    null: str = "null"
    labels: list[Label | Offset | Title | Alias] = field(default_factory=list)

    def as_string(self, label: Label | Offset) -> str:
        def and_name(prefix):
            return prefix + ":" + label.name

        match label:
            case AssetLabel(name):
                return and_name(self.asset)
            case LiabilityLabel(name):
                return and_name(self.liability)
            case CapitalLabel(name):
                return and_name(self.capital)
            case IncomeLabel(name):
                return and_name(self.income)
            case ExpenseLabel(name):
                return and_name(self.expense)
            case IncomeSummaryLabel(name):
                return and_name(self.income_summary)
            case RetainedEarningsLabel(name):
                return and_name(self.retained_earnings)
            case NullLabel(name):
                return and_name(self.null)
            case Offset(name, contra):
                return f"{self.contra}:{name}:{contra}"
            case _:
                raise ValueError(f"Invalid label: {label}.")

    def add(self, label_str: str):
        match label_str.strip().lower().split(":"):
            case [self.asset, name]:
                label: (Label | Offset) = AssetLabel(name)
            case [self.liability, name]:
                label = LiabilityLabel(name)
            case [self.capital, name]:
                label = CapitalLabel(name)
            case [self.income, name]:
                label = IncomeLabel(name)
            case [self.expense, name]:
                label = ExpenseLabel(name)
            case [self.income_summary, name]:
                label = IncomeSummaryLabel(name)
            case [self.retained_earnings, name]:
                label = RetainedEarningsLabel(name)
            case [self.null, name]:
                label = NullLabel(name)
            case [self.contra, name, contra_name]:
                label = Offset(name, contra_name)
            case _:
                raise ValueError(f"Invalid label: {label_str}.")
        self.labels.append(label)
        return self

    def add_many(self, labels: list[str], prefix: str = ""):
        if prefix and not prefix.endswith(":"):
            prefix = prefix.strip() + ":"
        for label in labels:
            self.add(prefix + label)
        return self

    def name(self, name: str, title: str):
        self.labels.append(Title(name, title))
        return self

    def alias(self, operation: str, debit: str, credit: str):
        self.labels.append(Alias(operation, debit, credit))
        return self

    def filter(self, cls: type[Label]):
        return [label for label in self.labels if isinstance(label, cls)]

    def filter_names(self, cls: type[Label]):
        return [label.name for label in self.labels if isinstance(label, cls)]

    def filter_last(self, cls: type[Label]):
        return self.filter_names(cls)[-1]


def base():
    return (
        Composer()
        .add("isa:current_profit")
        .add("re:retained_earnings")
        .add("null:null")
    )


class Chart(BaseModel):
    """Chart of accounts."""

    income_summary_account: str
    retained_earnings_account: str
    null_account: str
    assets: list[str] = []
    expenses: list[str] = []
    capital: list[str] = []
    liabilities: list[str] = []
    income: list[str] = []
    contra_accounts: dict[str, list[str]] = {}
    titles: dict[str, str] = {}
    operations: dict[str, tuple[str, str]] = {}

    def _contra(self, name, cls):
        return [
            (contra_name, cls) for contra_name in self.contra_accounts.get(name, [])
        ]

    def _recontra(self, name, cls):
        return [
            (name, contra_name, cls)
            for contra_name in self.contra_accounts.get(name, [])
        ]

    def ledger(self):
        from abacus import Ledger

        return Ledger((name, account()) for name, account in t_account_tuples(self))

    def get_label(self, name: str, composer=Composer()) -> str:
        label = dict(map(naming, to_labels(self)))[name]
        return composer.as_string(label)

    def contra_account_pairs(self, cls: Type[accounts.ContraAccount]):
        """Provide importmation for  closing entries."""
        return [
            (a, b)
            for (a, b, this_cls) in contra_account_pairs_all(self)
            if this_cls.__name__ == cls.__name__ # same class
        ]


def naming(label):
    if isinstance(label, Offset):
        return label.contra, label
    else:
        return label.name, label


def to_chart(composer: Composer) -> Chart:
    return Chart(
        income_summary_account=composer.filter_last(IncomeSummaryLabel),
        retained_earnings_account=composer.filter_last(RetainedEarningsLabel),
        null_account=composer.filter_last(NullLabel),
        assets=composer.filter_names(AssetLabel),
        expenses=composer.filter_names(ExpenseLabel),
        capital=composer.filter_names(CapitalLabel),
        liabilities=composer.filter_names(LiabilityLabel),
        income=composer.filter_names(IncomeLabel),
        contra_accounts=aggregate_offsets(composer),
        titles={label.name: label.title for label in composer.filter(Title)},
        operations={
            label.operation: (label.debit, label.credit)
            for label in composer.filter(Alias)
        },
    )


def aggregate_offsets(composer: Composer) -> dict[str, list[str]]:
    return {
        fst: [x[1] for x in xs]
        for fst, xs in groupby(
            [(off.name, off.contra) for off in incoming.filter(Offset)], lambda x: x[0]
        )
    }


def to_labels(chart) -> list[Label | Offset]:
    return chain(
        map(AssetLabel, chart.assets),
        map(LiabilityLabel, chart.liabilities),
        map(ExpenseLabel, chart.expenses),
        map(CapitalLabel, chart.capital),
        map(IncomeLabel, chart.income),
        [
            IncomeSummaryLabel(chart.income_summary_account),
            RetainedEarningsLabel(chart.retained_earnings_account),
            NullLabel(chart.null_account),
        ],
        [
            Offset(name, contra)
            for name, contra_names in chart.contra_accounts.items()
            for contra in contra_names
        ],
    )


def t_account_tuples(chart: Chart) -> Iterable[tuple[str, Type[accounts.TAccount]]]:
    """List account with offsets for ledger creation."""
    for name in chart.assets:
        yield name, accounts.Asset
        yield from chart._contra(name, accounts.ContraAsset)
    for name in chart.expenses:
        yield name, accounts.Expense
        yield from chart._contra(name, accounts.ContraExpense)
    for name in chart.capital:
        yield name, accounts.Capital
        yield from chart._contra(name, accounts.ContraCapital)
    for name in chart.liabilities:
        yield name, accounts.Liability
        yield from chart._contra(name, accounts.ContraLiability)
    for name in chart.income:
        yield name, accounts.Income
        yield from chart._contra(name, accounts.ContraIncome)
    yield chart.income_summary_account, accounts.IncomeSummaryAccount
    yield chart.retained_earnings_account, accounts.RetainedEarnings
    yield chart.null_account, accounts.NullAccount


def contra_account_pairs_all(
    chart: Chart,
) -> Iterable[tuple[str, str, Type[accounts.ContraAccount]]]:
    """List regular labels with offsets."""
    for name in chart.assets:
        yield from chart._recontra(name, accounts.ContraAsset)
    for name in chart.expenses:
        yield from chart._recontra(name, accounts.ContraExpense)
    for name in chart.capital:
        yield from chart._recontra(name, accounts.ContraCapital)
    for name in chart.liabilities:
        yield from chart._recontra(name, accounts.ContraLiability)
    for name in chart.income:
        yield from chart._recontra(name, accounts.ContraIncome)

#TODO: move below to tests

incoming = (
    base()
    .add("asset:cash")
    .add("capital:equity")
    .add_many(["cogs", "sga"], prefix="expense")
    .name("cogs", "Cost of goods sold")
    .name("sga", "Selling, general, and adm. expenses")
    .add("contra:equity:ts")
    .name("ts", "Treasury share")
    .add("income:sales")
    .add_many(["refunds", "voids"], prefix="contra:sales")
    .add("asset:ar")
    .alias("invoice", "ar", "sales")
    .alias("accept", "cash", "ar")
    .add("asset:inventory")
    .alias("cost", "cogs", "inventory")
    .alias("purchase", "inventory", "cash")
    .alias("refund", "refunds", "cash")
    .add_many(["dd", "ar"], prefix="liability")
)

assert incoming.as_string(AssetLabel("cash")) == "asset:cash"
assert aggregate_offsets(incoming) == {"equity": ["ts"], "sales": ["refunds", "voids"]}
assert to_chart(incoming).dict() == {
    "income_summary_account": "current_profit",
    "retained_earnings_account": "retained_earnings",
    "null_account": "null",
    "assets": ["cash", "ar", "inventory"],
    "expenses": ["cogs", "sga"],
    "capital": ["equity"],
    "liabilities": ["dd", "ar"],
    "income": ["sales"],
    "contra_accounts": {"equity": ["ts"], "sales": ["refunds", "voids"]},
    "titles": {
        "cogs": "Cost of goods sold",
        "sga": "Selling, general, and adm. expenses",
        "ts": "Treasury share",
    },
    "operations": {
        "invoice": ("ar", "sales"),
        "accept": ("cash", "ar"),
        "cost": ("cogs", "inventory"),
        "purchase": ("inventory", "cash"),
        "refund": ("refunds", "cash"),
    },
}


chart = to_chart(incoming)
assert isinstance(chart.ledger(), Ledger)
assert chart.contra_account_pairs(accounts.ContraIncome) == [
    ("sales", "refunds"),
    ("sales", "voids"),
]
assert list(to_labels(chart))[-1] == Offset(name="sales", contra="voids")
assert chart.get_label("sales") == "income:sales"
assert chart.get_label("refunds") == "contra:sales:refunds"
