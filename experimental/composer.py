from dataclasses import dataclass
from typing import Type

from pydantic import BaseModel

import abacus.engine.accounts as accounts  # type: ignore
from abacus.engine.accounts import ContraAccount  # type: ignore


@dataclass
class Label:
    """Parent class to hold an account name."""

    name: str

    def as_string(self, prefix: str):
        return prefix + ":" + self.name


@dataclass
class Offset:
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


class RetainedEarningsLabel(Label):
    pass


class IncomeSummaryLabel(Label):
    pass


class NullLabel(Label):
    pass


class Composer(BaseModel):
    """Extract and compose labels using prefixes.

    Examples:

      - in 'asset:cash' prefix is 'asset' and 'cash' is the name of the account.
      - in 'contra:equity:ta' prefix is 'contra', 'equity' account name and 'ta' is the contra account.

    """

    asset: str = "asset"
    capital: str = "capital"
    liability: str = "liability"
    income: str = "income"
    expense: str = "expense"
    contra: str = "contra"
    income_summary: str = "isa"
    retained_earnings: str = "re"
    null: str = "null"

    def _get_prefix(self, label: Label | Offset) -> str:
        match label:
            case AssetLabel(_):
                return self.asset
            case LiabilityLabel(_):
                return self.liability
            case CapitalLabel(_):
                return self.capital
            case IncomeLabel(_):
                return self.income
            case ExpenseLabel(_):
                return self.expense
            case IncomeSummaryLabel(_):
                return self.income_summary
            case RetainedEarningsLabel(_):
                return self.retained_earnings
            case NullLabel(_):
                return self.null
            case Offset(_, _):
                return self.contra
            case _:
                raise ValueError(f"Invalid label: {label}.")

    def _get_label_class(self, prefix: str):
        match prefix:
            case self.asset:
                return AssetLabel
            case self.liability:
                return LiabilityLabel
            case self.capital:
                return CapitalLabel
            case self.income:
                return IncomeLabel
            case self.expense:
                return ExpenseLabel
            case self.income_summary:
                return IncomeSummaryLabel
            case self.retained_earnings:
                return RetainedEarningsLabel
            case self.null:
                return NullLabel
            case _:
                raise ValueError(f"Invalid label: {prefix}.")

    def as_string(self, label: Label | Offset) -> str:
        prefix = self._get_prefix(label)
        return label.as_string(prefix)

    def extract(self, label_str: str) -> Label | Offset:
        match label_str.strip().lower().split(":"):
            case [prefix, name]:
                return self._get_label_class(prefix)(name)
            case [self.contra, account_name, contra_account_name]:
                return Offset(contra_account_name, account_name)
            case _:
                raise ValueError(f"Invalid label: {label_str}.")


@dataclass
class ChartList:
    accounts: list[Label | Offset]

    def names(self):
        return [account.name for account in self.accounts]

    @property
    def labels(self):
        return [account for account in self.accounts if isinstance(account, Label)]

    def safe_append(self, label):
        if label.name in self.names():
            raise ValueError(f"Duplicate account name: {label.name}.")
        if isinstance(label, Offset) and label.offsets not in self.names():
            raise ValueError(
                f"Account name must be defined before offsetting: {label.offsets}."
            )
        self.accounts.append(label)
        return self

    def add(self, label_string: str, composer=Composer()):
        return self.safe_append(label=composer.extract(label_string))

    def filter(self, cls: Type[Label] | Type[Offset]):
        return [account for account in self.accounts if isinstance(account, cls)]

    def filter_name(self, cls: Type[Label]):
        return [account.name for account in self.accounts if isinstance(account, cls)]

    def to_base_chart(self):
        return BaseChart(
            income_summary_account=self.isa,
            retained_earnings_account=self.re,
            null_account=self.null,
            assets=self.assets,
            liabilities=self.liabilities,
            capital=self.capital,
            income=self.income,
            expenses=self.expenses,
            contra_accounts=self.contra_accounts,
        )

    @property
    def isa(self):
        return self.get_exactly_one(IncomeSummaryLabel)

    @property
    def re(self):
        return self.get_exactly_one(RetainedEarningsLabel)

    @property
    def null(self):
        return self.get_exactly_one(NullLabel)

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

    @property
    def contra_accounts(self):
        return {
            # label.offset: [offset.name for offset in self.offsets(label.name)]
            # for label in self.labels
            # if self.offsets(label.name)
        }

    def offsets(self, name: str):
        return [offset for offset in self.filter(Offset) if offset.offsets == name]

    def get_exactly_one(self, cls: Type[Label]):
        matches = self.filter(cls)
        match len(matches):
            case 1:
                return matches[0].name
            case _:
                raise ValueError(
                    f"Expected exactly one {cls.__name__}, found {len(matches)}."
                )

    def stream(self, label_class, account_class, contra_account_class):
        for label in self.filter(label_class):
            yield label.name, account_class
            for offset in self.offsets(label.name):
                yield offset.name, contra_account_class

    def t_accounts(self):
        yield from self.stream(AssetLabel, accounts.Asset, accounts.ContraAsset)
        yield from self.stream(CapitalLabel, accounts.Capital, accounts.ContraCapital)
        yield from self.stream(
            LiabilityLabel, accounts.Liability, accounts.ContraLiability
        )
        yield from self.stream(IncomeLabel, accounts.Income, accounts.ContraIncome)
        yield from self.stream(ExpenseLabel, accounts.Expense, accounts.ContraExpense)
        yield self.get_exactly_one(IncomeSummaryLabel), accounts.IncomeSummaryAccount
        yield self.get_exactly_one(RetainedEarningsLabel), accounts.RetainedEarnings
        yield self.get_exactly_one(NullLabel), accounts.NullAccount

    def ledger_dict(self):
        return {name: t_account() for name, t_account in self.t_accounts()}

    def contra_pairs(self, cls: Type[ContraAccount]) -> list[str, str]:
        klass = {
            "ContraAsset": AssetLabel,
            "ContraLiability": LiabilityLabel,
            "ContraCapital": CapitalLabel,
            "ContraExpense": ExpenseLabel,
            "ContraIncome": IncomeLabel,
        }[cls.__name__]
        return [
            (offset.offsets, offset.name)
            for label in self.filter(klass)
            for offset in self.offsets(label.name)
        ]

    def as_dict(self):
        return {account.unique_name(): account for account in self.accounts}

    def label(self, name):
        return self.as_dict()[name]


def base_chart_list():
    return ChartList(
        [
            IncomeSummaryLabel("current_profit"),
            RetainedEarningsLabel("retained_earnings"),
            NullLabel("null"),
        ]
    )


class BaseChart(BaseModel):
    income_summary_account: str
    retained_earnings_account: str
    null_account: str
    assets: list[str] = []
    expenses: list[str] = []
    capital: list[str] = []
    liabilities: list[str] = []
    income: list[str] = []
    contra_accounts: dict[str, list[str]] = {}

    def to_chart_list(self):
        chart_list = ChartList(
            [
                IncomeSummaryLabel(self.income_summary_account),
                RetainedEarningsLabel(self.retained_earnings_account),
                NullLabel(self.null_account),
            ]
        )
        for name in self.assets:
            chart_list.safe_append(AssetLabel(name))
        for name in self.liabilities:
            chart_list.safe_append(LiabilityLabel(name))
        for name in self.capital:
            chart_list.safe_append(CapitalLabel(name))
        for name in self.income:
            chart_list.safe_append(IncomeLabel(name))
        for name in self.expenses:
            chart_list.safe_append(ExpenseLabel(name))
        for name, contra_names in self.contra_accounts.items():
            for contra in contra_names:
                chart_list.safe_append(Offset(name, contra))
        return chart_list

    def safe_append(self, attribute, value):
        if value in self.account_names():
            raise ValueError(f"Duplicate account name: {value}.")
        getattr(self, attribute).append(value)

    def add(self, label_str: str, composer=Composer()):
        return self.promote(label=composer.extract(label_str))

    def promote(self, label: Label | Offset):
        match label:
            case AssetLabel(name):
                self.safe_append("assets", name)
            case LiabilityLabel(name):
                self.safe_append("liabilities", name)
            case CapitalLabel(name):
                self.safe_append("capital", name)
            case IncomeLabel(name):
                self.safe_append("income", name)
            case ExpenseLabel(name):
                self.safe_append("expenses", name)
            case IncomeSummaryLabel(name):
                self.income_summary_account = name
            case RetainedEarningsLabel(name):
                self.retained_earnings_account = name
            case NullLabel(name):
                self.null_account = name
            case Offset(name, contra):
                self.contra_accounts.setdefault(name, []).append(contra)
        return self

    def t_accounts(self):
        mapper = [
            ("assets", accounts.Asset, accounts.ContraAsset),
            ("capital", accounts.Capital, accounts.ContraCapital),
            ("liabilities", accounts.Liability, accounts.ContraLiability),
            ("income", accounts.Income, accounts.ContraIncome),
            ("expenses", accounts.Expense, accounts.ContraExpense),
        ]
        for attribute, cls, contra_cls in mapper:
            for name in getattr(self, attribute):
                yield name, cls
                for contra_name in self.contra_accounts.get(name, []):
                    yield contra_name, contra_cls
        yield self.income_summary_account, accounts.IncomeSummaryAccount
        yield self.retained_earnings_account, accounts.RetainedEarnings
        yield self.null_account, accounts.NullAccount

    def account_names(self):
        return [name for name, _ in self.t_accounts()]

    def contra_pairs(self, cls: Type[ContraAccount]):
        mapper = {
            "ContraAsset": "assets",
            "ContraLiability": "liabilities",
            "ContraCapital": "capital",
            "ContraExpense": "expenses",
            "ContraIncome": "income",
        }
        names = getattr(self, mapper[cls.__name__])
        return [
            (name, contra_name)
            for name in names
            for contra_name in self.contra_accounts.get(name, [])
        ]

    def label(self, account_name) -> Label | Offset:
        if account_name in self.assets:
            return AssetLabel(account_name)
        elif account_name in self.liabilities:
            return LiabilityLabel(account_name)
        elif account_name in self.capital:
            return CapitalLabel(account_name)
        elif account_name in self.income:
            return IncomeLabel(account_name)
        elif account_name in self.expenses:
            return ExpenseLabel(account_name)
        elif account_name == self.income_summary_account:
            return IncomeSummaryLabel(account_name)
        elif account_name == self.retained_earnings_account:
            return RetainedEarningsLabel(account_name)
        elif account_name == self.null_account:
            return NullLabel(account_name)
        for name, contra_names in self.contra_accounts.items():
            if account_name in contra_names:
                return Offset(name, account_name)
        raise ValueError(f"Invalid account name: {account_name}.")


def base():
    return BaseChart(
        income_summary_account="current_profit",
        retained_earnings_account="retained_earnings",
        null_account="null",
    )


class ReChart(BaseModel):
    base: ChartList = base_chart_list()
    titles: dict[str, str] = {}
    operations: dict[str, tuple[str, str]] = {}
    composer: Composer = Composer()

    def asset(self, name: str):
        self.base.safe_append(AssetLabel(name))
        return self

    def liability(self, name: str):
        self.base.safe_append(LiabilityLabel(name))
        return self

    def capital(self, name: str):
        self.base.safe_append(CapitalLabel(name))
        return self

    def income(self, name: str):
        self.base.safe_append(IncomeLabel(name))
        return self

    def expense(self, name: str):
        self.base.safe_append(ExpenseLabel(name))
        return self

    def add(self, label_str: str):
        self.base.add(label_str, self.composer)
        return self

    def add_many(self, labels: list[str], prefix: str = ""):
        if prefix and not prefix.endswith(":"):
            prefix = prefix.strip() + ":"
        for label in labels:
            self.add(prefix + label)
        return self

    def offset(self, name: str, contra: str):
        self.base.safe_append(Offset(name, contra))
        return self

    def offset_many(self, name: str, contra_names: str):
        for contra in contra_names:
            self.offset(name, contra)
        return self

    def name(self, name: str, title: str):
        self.titles[name] = title
        return self

    def alias(self, operation: str, debit: str, credit: str):
        self.operations[operation] = (debit, credit)
        return self

    def label(self, account_name) -> str:
        return self.composer.as_string(self.base.label(account_name))


class Chart(BaseModel):
    base: BaseChart = base()
    titles: dict[str, str] = {}
    operations: dict[str, tuple[str, str]] = {}
    composer: Composer = Composer()

    def asset(self, name: str):
        self.base.promote(AssetLabel(name))
        return self

    def liability(self, name: str):
        self.base.promote(LiabilityLabel(name))
        return self

    def capital(self, name: str):
        self.base.promote(CapitalLabel(name))
        return self

    def income(self, name: str):
        self.base.promote(IncomeLabel(name))
        return self

    def expense(self, name: str):
        self.base.promote(ExpenseLabel(name))
        return self

    def add(self, label_str: str):
        self.base.add(label_str, self.composer)
        return self

    def add_many(self, labels: list[str], prefix: str = ""):
        if prefix and not prefix.endswith(":"):
            prefix = prefix.strip() + ":"
        for label in labels:
            self.add(prefix + label)
        return self

    def offset(self, name: str, contra: str):
        self.base.promote(Offset(name, contra))
        return self

    def offset_many(self, name: str, contra_names: str):
        for contra in contra_names:
            self.offset(name, contra)
        return self

    def name(self, name: str, title: str):
        self.titles[name] = title
        return self

    def alias(self, operation: str, debit: str, credit: str):
        self.operations[operation] = (debit, credit)
        return self

    def label(self, account_name) -> str:
        return self.composer.as_string(self.base.label(account_name))

    def ledger(self):
        from ledger import Ledger

        return Ledger(
            data={name: t_account() for name, t_account in self.base.t_accounts()},
            chart=self,
        )


def create_chart(
    assets=None, liabilities=None, capital=None, income=None, expenses=None
):
    base_chart = base()
    base_chart.assets = assets if assets else []
    base_chart.liabilities = liabilities if liabilities else []
    base_chart.capital = capital if capital else []
    base_chart.income = income if income else []
    base_chart.expenses = expenses if expenses else []
    return Chart(base=base_chart)


# TODO: must check downstream usage of Ledger.chart (creation vs presentation part)
#       "and decide if it should be a Chart or a BaseChart"
