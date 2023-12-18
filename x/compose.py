from dataclasses import dataclass, field
from typing import Callable, Iterable, Type
from pydantic import BaseModel

import accounts  # type: ignore
from accounts import ContraAccount, TAccount  # type: ignore
from base import AbacusError, Entry
from report import Column


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

    This class helps in internationalisation - it will allow labels like 'актив:касса'.

    Examples:
      - in 'asset:cash' prefix is 'asset' and 'cash' is the name of the account.
      - in 'contra:equity:ta' prefix is 'contra', 'equity' is account name and 'ta' is the new contra account.

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
class ChartList:
    income_summary_account: str
    retained_earnings_account: str
    null_account: str
    accounts: list[Label | ContraLabel]

    def names(self):
        return [
            self.income_summary_account,
            self.retained_earnings_account,
            self.null_account,
        ] + [account.name for account in self.accounts]

    @property
    def labels(self):
        return [account for account in self.accounts if isinstance(account, Label)]

    @property
    def contra_labels(self):
        return [
            account for account in self.accounts if isinstance(account, ContraLabel)
        ]

    def safe_append(self, label):
        if label.name in self.names():
            raise AbacusError(
                f"Duplicate account name detected, name already in use: {label.name}."
            )
        if isinstance(label, ContraLabel) and label.offsets not in self.names():
            raise AbacusError(
                f"Account name must be defined before adding contra account: {label.offsets}."
            )
        self.accounts.append(label)
        return self

    def add(self, label_string: str, composer=Composer()):
        return self.safe_append(label=composer.extract(label_string))

    def add_many(self, label_strings: list[str], composer=Composer()):
        for s in label_strings:
            self.add(s, composer)
        return self

    def filter(self, cls: Type[Label] | Type[ContraLabel]):
        return [account for account in self.accounts if isinstance(account, cls)]

    def filter_name(self, cls: Type[Label]):
        return [account.name for account in self.accounts if isinstance(account, cls)]

    @property
    def assets(self):
        return self.filter_name(AssetLabel)

    @property
    def liabilities(self):
        return self.filter_name(LiabilityLabel)

    @property
    def capital(self):
        return self.filter_name(CapitalLabel)

    @property
    def income(self):
        return self.filter_name(IncomeLabel)

    @property
    def expenses(self):
        return self.filter_name(ExpenseLabel)

    def _find_contra_labels(self, name: str):
        return [
            contra_label
            for contra_label in self.filter(ContraLabel)
            if contra_label.offsets == name
        ]

    def stream(self, label_class, account_class, contra_account_class):
        """Yield tuples of account names and account or contra account classes."""
        for label in self.filter(label_class):
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
        """Retrun list of account name-contra account name pairs for a given contra account class."""
        klass = {
            "ContraAsset": AssetLabel,
            "ContraLiability": LiabilityLabel,
            "ContraCapital": CapitalLabel,
            "ContraExpense": ExpenseLabel,
            "ContraIncome": IncomeLabel,
        }[cls.__name__]
        return [
            contra_label
            for label in self.filter(klass)
            for contra_label in self._find_contra_labels(label.name)
        ]

    def __getitem__(self, account_name: str) -> Label | ContraLabel:
        return {account.name: account for account in self.accounts}[account_name]


def make_chart(*strings: list[str]):
    return ChartList(
        income_summary_account="current_profit",
        retained_earnings_account="retained_earnings",
        null_account="null",
        accounts=[],
    ).add_many(strings)


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

    def items(self):
        return self.data.items()

    def subset(self, cls):
        """Filter ledger by account type."""
        return BaseLedger(
            {
                account_name: t_account
                for account_name, t_account in self.data.items()
                if isinstance(t_account, cls)
            }
        )


def closing_contra_entries(chart, ledger, contra_cls):
    """Yield entries that will close contra accounts of a given type `contra_cls`."""
    for contra_label in chart.contra_pairs(contra_cls):
        yield ledger.data[contra_label.name].transfer(contra_label.name, contra_label.offsets)  # type: ignore


def close_to_income_summary_account(chart, ledger, cls):
    """Yield entries that will close income or expense accounts to income summary account."""
    for name, account in ledger.data.items():
        if isinstance(account, cls):
            yield account.transfer(name, chart.income_summary_account)


def close_first(chart: ChartList, ledger: BaseLedger) -> tuple[BaseLedger, list[Entry]]:
    """Close contra income and contra expense accounts."""
    c1 = closing_contra_entries(chart, ledger, accounts.ContraIncome)
    c2 = closing_contra_entries(chart, ledger, accounts.ContraExpense)
    closing_entries = list(c1) + list(c2)
    return ledger.post_many(closing_entries), closing_entries


def close_second(
    chart: ChartList, dummy_ledger: BaseLedger
) -> tuple[BaseLedger, list[Entry]]:
    """Close income and expense accounts to income summary account ("income_summary_account"),
    then close income_summary_account to retained earnings."""
    # Close income and expense to income_summary_account
    a = close_to_income_summary_account(chart, dummy_ledger, accounts.Income)
    b = close_to_income_summary_account(chart, dummy_ledger, accounts.Expense)
    closing_entries = list(a) + list(b)
    dummy_ledger.post_many(closing_entries)
    # Close income_summary_account to retained earnings
    isa, re = chart.income_summary_account, chart.retained_earnings_account
    b = dummy_ledger.data[isa].balance()
    closing_entries.append(Entry(debit=isa, credit=re, amount=b))
    return dummy_ledger.post_many(closing_entries), closing_entries


def close_last(chart: ChartList, ledger: BaseLedger) -> tuple[BaseLedger, list[Entry]]:
    """Close permanent contra accounts."""
    c3 = closing_contra_entries(chart, ledger, accounts.ContraAsset)
    c4 = closing_contra_entries(chart, ledger, accounts.ContraLiability)
    c5 = closing_contra_entries(chart, ledger, accounts.ContraCapital)
    closing_entries = list(c3) + list(c4) + list(c5)
    return ledger.post_many(closing_entries), closing_entries


def chain(chart, ledger, functions):
    _ledger = ledger.condense()
    closing_entries = []
    for f in functions:
        _ledger, entries = f(chart, _ledger)
        closing_entries += entries
    return _ledger, closing_entries


def view_trial_balance(chart, ledger) -> str:
    data = list(yield_tuples_for_trial_balance(chart, ledger))

    col_1 = Column([d[0] for d in data]).align_left(".").add_space(1).header("Account")
    col_2 = nth(data, 1).align_right().add_space_left(2).header("Debit").add_space(2)
    col_3 = nth(data, 2).align_right().add_space_left(2).header("Credit")
    return (col_1 + col_2 + col_3).printable()


class _BalanceSheet(BaseModel):
    assets: dict[str, int]
    capital: dict[str, int]
    liabilities: dict[str, int]


class _IncomeStatement(BaseModel):
    income: dict[str, int]
    expenses: dict[str, int]


from collections import UserDict


class TB(UserDict[str, tuple[int, int]]):
    ...


def make_trial_balance(chart, ledger):
    return TB(
        {name: (a, b) for name, a, b in yield_tuples_for_trial_balance(chart, ledger)}
    )


@dataclass
class Reporter:
    chart: ChartList
    ledger: BaseLedger
    titles: dict[str, str] = field(default_factory=dict)

    def income_statement(self, header="Income Statement"):
        from report import IncomeStatement, IncomeStatementViewer

        ledger, _ = chain(self.chart, self.ledger, [close_first])
        statement = IncomeStatement.new(ledger)
        return IncomeStatementViewer(statement, self.titles, header)

    def balance_sheet(self, header="Balance Sheet"):
        from report import BalanceSheet, BalanceSheetViewer

        ledger, _ = chain(
            self.chart, self.ledger, [close_first, close_second, close_last]
        )
        statement = BalanceSheet.new(ledger)
        return BalanceSheetViewer(statement, self.titles, header)

    def trial_balance(self, header="Trial Balance"):
        # ledger, _ = chain(self.chart, self.ledger, [])
        print(self.ledger.data["salaries"])
        return view_trial_balance(self.chart, self.ledger)

    def tb(self):
        return make_trial_balance(self.chart, self.ledger)


def yield_tuples_for_trial_balance(chart, ledger):
    def must_exclude(t_account):
        return any(
            [
                isinstance(t_account, e)
                for e in [accounts.NullAccount, accounts.IncomeSummaryAccount]
            ]
        )

    for account_name, t_account in ledger.items():
        if isinstance(t_account, accounts.DebitAccount) and not must_exclude(t_account):
            yield account_name, t_account.balance(), 0
    for account_name, t_account in ledger.items():
        if isinstance(t_account, accounts.CreditAccount) and not must_exclude(
            t_account
        ):
            yield account_name, 0, t_account.balance()


def nth(data, n: int, f=str) -> Column:
    """Make a column from nth element of each tuple or list in `data`."""
    return Column([f(d[n]) for d in data])
