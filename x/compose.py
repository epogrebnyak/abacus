from collections import UserDict
from dataclasses import dataclass, field
from typing import Callable, Iterable, Type

import accounts  # type: ignore
from accounts import ContraAccount, TAccount  # type: ignore
from base import AbacusError, Entry
from pydantic import BaseModel
from report import Column

# TODO: требуется code review c позиций читаемости 
#       и поддерживаемости кода
#       под ревью compose.py, test_compose.py, using.py
#       приветствуются идеи новых тестов

@dataclass
class Label:
    """Base class to hold an account name."""

    name: str

    def as_string(self, prefix: str):
        return prefix + ":" + self.name


@dataclass
class ContraLabel:
    """Class to add contra account."""

    name: str
    offsets: str

    def as_string(self, prefix: str):
        return prefix + ":" + self.offsets + ":" + self.name


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


class Composer(BaseModel):
    """Extract and compose labels using prefixes.

    This class helps in internationalisation - it allows
    working with labels like 'актив:касса'.

    Examples:
      - in 'asset:cash' prefix is 'asset' and 'cash' is the name of the account.
      - in 'contra:equity:ta' prefix is 'contra', 'equity' is account name and
        'ta' is the new contra account.

    """

    asset: str = "asset"
    capital: str = "capital"
    liability: str = "liability"
    income: str = "income"
    expense: str = "expense"
    contra: str = "contra"
    # FIXME: special treatment needed for "capital:retained_earnings"
    # income_summary: str = "income_summary_account"
    # retained_earnings: str = "re"
    # null: str = "null"

    def as_string(self, label: Label | ContraLabel) -> str:
        return label.as_string(prefix(self, label))

    def extract(self, label_string: str) -> Label | ContraLabel:
        match label_string.strip().lower().split(":"):
            case [prefix, name]:
                return label_class(self, prefix)(name)  # type: ignore
            case [self.contra, account_name, contra_account_name]:
                return ContraLabel(contra_account_name, account_name)
            case _:
                raise AbacusError(f"Invalid label: {label_string}.")


def prefix(composer: Composer, label: Label | ContraLabel) -> str:
    """Return prefix string given a label or contra label."""
    match label:
        case AssetLabel(_):
            return composer.asset
        case LiabilityLabel(_):
            return composer.liability
        case CapitalLabel(_):
            return composer.capital
        case IncomeLabel(_):
            return composer.income
        case ExpenseLabel(_):
            return composer.expense
        case ContraLabel(_, _):
            return composer.contra
        case _:
            raise AbacusError(f"Invalid label: {label}.")


def label_class(composer: Composer, prefix: str) -> Type[Label | ContraLabel]:
    """Return label or contra label class contructor given the prefix string."""
    match prefix:
        case composer.asset:
            return AssetLabel
        case composer.liability:
            return LiabilityLabel
        case composer.capital:
            return CapitalLabel
        case composer.income:
            return IncomeLabel
        case composer.expense:
            return ExpenseLabel
        case _:
            raise AbacusError(f"Invalid label: {prefix}.")


@dataclass
class BaseChart:
    income_summary_account: str
    retained_earnings_account: str
    null_account: str
    labels: list[Label]
    contra_labels: list[ContraLabel]

    @property
    def all_labels(self):
        return self.labels + self.contra_labels

    def names(self) -> list[str]:
        return [
            self.income_summary_account,
            self.retained_earnings_account,
            self.null_account,
        ] + [account.name for account in self.all_labels]

    def safe_append(self, label):
        if label.name in self.names():
            raise AbacusError(
                f"Duplicate account name detected, name already in use: {label.name}."
            )
        match label:
            case Label(_):
                self.labels.append(label)
            case ContraLabel(_, offsets):
                if offsets in self.names():
                    self.contra_labels.append(label)
                else:
                    raise AbacusError(
                        f"Must define account name before adding contra account to it: {label.offsets}."
                    )
        return self

    def add(self, label_string: str, composer=Composer()):
        return self.safe_append(label=composer.extract(label_string))

    def add_many(self, label_strings: list[str], composer=Composer()):
        for s in label_strings:
            self.add(s, composer)
        return self

    def _filter(self, cls):
        return [label for label in self.labels if isinstance(label, cls)]

    def _filter_name(self, cls: Type[Label]):
        return [account.name for account in self.labels if isinstance(account, cls)]

    @property
    def assets(self):
        return self._filter_name(AssetLabel)

    @property
    def liabilities(self):
        return self._filter_name(LiabilityLabel)

    @property
    def capital(self):
        return self._filter_name(CapitalLabel)

    @property
    def income(self):
        return self._filter_name(IncomeLabel)

    @property
    def expenses(self):
        return self._filter_name(ExpenseLabel)

    def _find_contra_labels(self, name: str):
        return [
            contra_label
            for contra_label in self.contra_labels
            if contra_label.offsets == name
        ]

    def stream(self, label_class, account_class, contra_account_class):
        """Yield tuples of account names and account or contra account classes."""
        for label in self._filter(label_class):
            yield label.name, account_class
            for contra_label in self._find_contra_labels(label.name):
                yield contra_label.name, contra_account_class

    def t_accounts(self):
        yield from self.stream(AssetLabel, accounts.Asset, accounts.ContraAsset)
        yield from self.stream(CapitalLabel, accounts.Capital, accounts.ContraCapital)
        yield from self.stream(
            LiabilityLabel, accounts.Liability, accounts.ContraLiability
        )
        yield from self.stream(IncomeLabel, accounts.Income, accounts.ContraIncome)
        yield from self.stream(ExpenseLabel, accounts.Expense, accounts.ContraExpense)
        yield self.income_summary_account, accounts.IncomeSummaryAccount
        yield self.retained_earnings_account, accounts.RetainedEarnings
        yield self.null_account, accounts.NullAccount

    def ledger_dict(self):
        return {name: t_account() for name, t_account in self.t_accounts()}

    def ledger(self):
        return BaseLedger(self.ledger_dict())

    def contra_pairs(self, cls: Type[ContraAccount]) -> list[ContraLabel]:
        """Return a list of account name - contra account name pairs for a given contra account class.
        Used in creating closing entries"""
        klass = {
            "ContraAsset": AssetLabel,
            "ContraLiability": LiabilityLabel,
            "ContraCapital": CapitalLabel,
            "ContraExpense": ExpenseLabel,
            "ContraIncome": IncomeLabel,
        }[cls.__name__]
        return [
            contra_label
            for label in self._filter(klass)
            for contra_label in self._find_contra_labels(label.name)
        ]

    def __getitem__(self, account_name: str) -> Label | ContraLabel:
        return {account.name: account for account in self.all_labels}[account_name]


def make_chart(*strings: list[str]):  # type: ignore
    return BaseChart(
        income_summary_account="current_profit",
        retained_earnings_account="retained_earnings",
        null_account="null",
        labels=[],
        contra_labels=[],
    ).add_many(
        strings
    )  # type: ignore


@dataclass
class BaseLedger:
    data: dict[str, TAccount]

    def post(self, debit, credit, amount) -> None:
        return self.post_one(Entry(debit, credit, amount))

    def post_one(self, entry: Entry):
        return self.post_many([entry])

    def post_many(self, entries: Iterable[Entry]):
        failed = []
        for entry in entries:
            try:
                self.data[entry.debit].debit(entry.amount)
                self.data[entry.credit].credit(entry.amount)
            except KeyError:
                failed.append(entry)
        if failed:
            raise AbacusError(failed)
        return self

    def create_with(self, f: Callable):
        """Create new ledger with each T-account transformed by `f`."""
        return BaseLedger(
            data={name: f(taccount) for name, taccount in self.data.items()}
        )

    def deep_copy(self):
        return self.create_with(lambda taccount: taccount.deep_copy())

    def condense(self):
        return self.create_with(lambda taccount: taccount.condense())

    def balances(self):
        return self.create_with(lambda taccount: taccount.balance()).data

    def nonzero_balances(self):
        return {k: v for k, v in self.balances().items() if v != 0}

    def subset(self, cls):
        """Filter ledger by account type."""
        return BaseLedger(
            {
                account_name: t_account
                for account_name, t_account in self.data.items()
                if isinstance(t_account, cls)
            }
        )

    def balance_sheet(self):
        from report import balance_sheet

        return balance_sheet(self)

    def income_statement(self):
        from report import income_statement

        return income_statement(self)


class Pipeline:
    """A pipeline to accumulate ledger transformations."""

    def __init__(self, chart: BaseChart, ledger: BaseLedger):
        self.chart = chart
        self.ledger = ledger.deep_copy()
        self.closing_entries: list[Entry] = []

    def append_and_post(self, entry: Entry):
        self.ledger.post_one(entry)
        self.closing_entries.append(entry)

    def close_contra(self, contra_cls):
        """Close contra accounts of a given type `contra_cls`"""
        for contra_label in self.chart.contra_pairs(contra_cls):
            account = self.ledger.data[contra_label.name]
            entry = account.transfer(contra_label.name, contra_label.offsets)
            self.append_and_post(entry)
        return self

    def close_to_isa(self, cls):
        """Close income or expense accounts to income summary account."""
        for name, account in self.ledger.data.items():
            if isinstance(account, cls):
                entry = account.transfer(name, self.chart.income_summary_account)
                self.append_and_post(entry)
        return self

    def close_isa_to_re(self):
        """Close income summary account to retained earnings account."""
        isa = self.chart.income_summary_account
        re = self.chart.retained_earnings_account
        entry = Entry(debit=isa, credit=re, amount=self.ledger.data[isa].balance())
        self.append_and_post(entry)
        return self

    def close_first(self):
        """Close contra income and contra expense accounts."""
        self.close_contra(accounts.ContraIncome)
        self.close_contra(accounts.ContraExpense)
        return self

    def close_second(self):
        """Close income and expense accounts to income summary account,
        then close income summary account to retained earnings."""
        self.close_to_isa(accounts.Income)
        self.close_to_isa(accounts.Expense)
        self.close_isa_to_re()
        return self

    def close_last(self):
        """Close permanent contra accounts."""
        self.close_contra(accounts.ContraAsset)
        self.close_contra(accounts.ContraLiability)
        self.close_contra(accounts.ContraCapital)
        return self

#FIXME: добавить класс TrialBalanceViewer 
class TrialBalance(UserDict[str, tuple[int, int]]):
    def column_1(self):
        names = [
            name.replace("_", " ").strip().capitalize() for name in self.data.keys()
        ]
        return Column(names).align_left(".").add_space(1).header("Account")

    def column_2(self):
        return (
            Column([str(d) for (d, _) in self.data.values()])
            .align_right()
            .add_space_left(2)
            .header("Debit")
            .add_space(2)
        )

    def column_3(self):
        return (
            Column([str(c) for (_, c) in self.data.values()])
            .align_right()
            .add_space_left(2)
            .header("Credit")
        )

    def table(self):
        return self.column_1() + self.column_2() + self.column_3()

    def view(self):
        return self.table().printable()


def yield_tuples(ledger):
    for name, taccount in ledger.subset(accounts.DebitAccount).data.items():
        yield name, taccount.balance(), 0
    for name, taccount in ledger.subset(accounts.CreditAccount).data.items():
        yield name, 0, taccount.balance()


def trial_balance(chart, ledger):
    ignore = [chart.null_account, chart.income_summary_account]
    return TrialBalance(
        {name: (a, b) for name, a, b in yield_tuples(ledger) if name not in ignore}
    )


@dataclass
class Reporter:
    chart: BaseChart
    ledger: BaseLedger
    titles: dict[str, str] = field(default_factory=dict)

    @property
    def pipeline(self):
        return Pipeline(self.chart, self.ledger)

    def income_statement(self, header="Income Statement"):
        p = self.pipeline.close_first()
        return p.ledger.income_statement().viewer(self.titles, header)

    def balance_sheet(self, header="Balance Sheet"):
        p = self.pipeline.close_first().close_second().close_last()
        return p.ledger.balance_sheet().viewer(self.titles, header)

    def trial_balance(self, header="Trial Balance"):
        return trial_balance(self.chart, self.ledger)
