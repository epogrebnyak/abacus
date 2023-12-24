from collections import UserDict

from dataclasses import dataclass, field  # NOTE: may use pydantic.dataclasses
from typing import Callable, Iterable, Type

import accounts  # type: ignore
from accounts import ContraAccount, TAccount  # type: ignore
from base import AbacusError, Entry
from pydantic import BaseModel
from report import Column

# xopowen
# у вас разделение логики идёт по типам классов.я про Label и наследников.
# я не совсем уверин в правелности данного подхода.
# тип Label зависит от prefix может это стоит учитывать пи создании Label
# но это личное впеетление на читабелность это не влияет. Но может повлият на поддерживаемости

# EP: c Label также не уверен что все совершенно правильно,
#     логика следующая - есть дефолтные префиксы на английском,
#     префиксы определят как распознатся текстовый идентификатор
#     типа "asset:cash". Если создать Composer с другими префиксами,
#     то и можно распознать строку типа "актив:наличные".

from abc import ABC, abstractmethod
from typing import ClassVar


@dataclass
class BaseLabel(ABC):
    name: str

    def as_string(self, prefix: str):
        return prefix + ":" + self.name


# xopowen
# этот класс тоже может наследуется от Label
# EP: можно наследовать он базового класса, от самоого Label нельзя,
#     потому что перестанет работать (в коде ниже)
# match label:
# case Label(_):
#     self.labels.append(label)
# case ContraLabel(_, offsets):
#     if offsets in self.names:
#         self.contra_labels.append(label)
#  но в целом согласен не так уж красиво


@dataclass
class RegularLabel(BaseLabel):
    """Class to hold a regular account name.
    Subclasses used to indicate account type."""

    def as_string(self, prefix: str = ""):
        return self.use_prefix(prefix) + ":" + self.name


class AssetLabel(RegularLabel):
    prefix = "asset"


class CapitalLabel(RegularLabel):
    prefix = "capital"


class LiabilityLabel(RegularLabel):
    prefix = "liability"


class ExpenseLabel(RegularLabel):
    prefix = "expense"


class IncomeLabel(RegularLabel):
    prefix = "income"


@dataclass
class ContraLabel(BaseLabel):
    """Class to add contra account name."""

    prefix = "contra"
    offsets: str

    def as_string(self, prefix: str = ""):
        return self.use_prefix(prefix) + ":" + self.offsets + ":" + self.name


# NOTE: may need special treatment needed for "capital:retained_earnings"
# income_summary: str = "income_summary_account"
# retained_earnings: str = "re"
# null: str = "null"


class Composer(BaseModel):
    """Create or serialise labels using prefixes.

    This class allows working with labels in
    languges other than English, for example
    like 'актив:касса' becomes possible.

    Examples:
      - in 'asset:cash' prefix is 'asset' and 'cash' is the name of the account;
      - in 'contra:equity:ta' prefix is 'contra', 'equity' is account name and 'ta' is the new contra account.
    """

    asset: str = AssetLabel.prefix
    capital: str = CapitalLabel.prefix
    liability: str = LiabilityLabel.prefix
    income: str = IncomeLabel.prefix
    expense: str = ExpenseLabel.prefix
    contra: str = ContraLabel.prefix

    @property
    def mapping(self):
        return [
            (self.asset, AssetLabel),
            (self.liability, LiabilityLabel),
            (self.capital, CapitalLabel),
            (self.income, IncomeLabel),
            (self.expense, ExpenseLabel),
            (self.contra, ContraLabel),
        ]

    def get_label_contructor(self, prefix: str) -> Type[RegularLabel | ContraLabel]:
        """Returns constructor for account or contra account label or raises exception."""
        try:
            return dict(self.mapping)[prefix]
        except KeyError:
            raise AbacusError(f"Invalid prefix: {prefix}.")

    def get_prefix(self, label: RegularLabel | ContraLabel) -> str:
        """Returns prefix string for a given account or contra account label."""
        for prefix, label_class in self.mapping:
            if isinstance(label, label_class):
                return prefix
        raise AbacusError(f"No prefix found for: {label}.")

    def extract(self, label_string: str) -> RegularLabel | ContraLabel:
        """Return Label or ContraLabel based on `label_string`.

        For example, for `asset:cash` string should produce `AssetLabel("cash")`.
        """
        match label_string.split(":"):
            case [prefix, name]:
                return self.get_label_contructor(prefix)(name)  # type: ignore
            #xopowen
            #так как  ContraLabel всё равно есть в mapping
            # case[self.contra, account_name, contra_account_name]:
                # return self.get_label_contructor(contra_account_name)(account_name)
            case [self.contra, account_name, contra_account_name]:
                return ContraLabel(contra_account_name, account_name)
            case _:
                raise AbacusError(f"Cannot parse label string: {label_string}.")

    def as_string(self, label: RegularLabel | ContraLabel) -> str:
        return label.as_string(prefix=self.get_prefix(label))


# xopowen
# довольно пышный  класс
# с точки зрения читабильности вопросов нет
# для поддершки нужно много тестов


@dataclass
class BaseChart:
    income_summary_account: str = "current_profit"
    retained_earnings_account: str = "retained_earnings"
    null_account: str = "null"
    regular_labels: list[RegularLabel] = field(default_factory=list)
    contra_labels: list[ContraLabel] = field(default_factory=list)

    # xopowen: эти функции очень связана с BaseChart возможно соить их поместить в него как staticmethod
    # также хаменить BaseChart на self.__class__ для возможности насделования
    @classmethod
    def use(cls, *strings: list[str]):
        return cls().add_many(strings)

    @property
    def labels(self) -> list[RegularLabel | ContraLabel]:
        return self.regular_labels + self.contra_labels

    @property
    def names(self) -> list[str]:
        return [
            self.income_summary_account,
            self.retained_earnings_account,
            self.null_account,
        ] + [account.name for account in self.labels]

    # уязвиемое место по возможности стоить подробно тестировать
    def safe_append(self, label):
        if label.name in self.names:
            raise AbacusError(
                f"Duplicate account name detected, name already in use: {label.name}."
            )
        match label:
            case RegularLabel(_):
                self.regular_labels.append(label)
            case ContraLabel(_, offsets):
                if offsets in self.names:
                    self.contra_labels.append(label)
                else:
                    raise AbacusError(
                        f"Must define account name before adding contra account to it: {label.offsets}."
                    )
        return self

    def add(self, label_string: str, composer: Composer | None = None):
        return self.add_many([label_string], composer)

    def add_many(self, label_strings: list[str], composer: Composer | None = None):
        if composer is None:
            composer = Composer()
        for s in label_strings:
            self.safe_append(label=composer.extract(s))
        return self

    def _filter(self, cls: Type[RegularLabel] | Type[ContraLabel]):
        return [label for label in self.labels if isinstance(label, cls)]

    def _filter_name(self, cls: Type[RegularLabel]):
        return [account.name for account in self.labels if isinstance(account, cls)]

    # TODO: create WritableChart class
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

    def _find_contra_labels(self, name: str) -> list[ContraLabel]:
        """Retrun a list of contra labels that offset a specific account *name*."""
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

    def __getitem__(self, account_name: str) -> RegularLabel | ContraLabel:
        # NOTE: will not show retained earnigns, isa and null accounts
        return {account.name: account for account in self.labels}[account_name]


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

    # TODO test this
    def deep_copy(self):
        return self.create_with(lambda taccount: taccount.deep_copy())

    # TODO test this
    def condense(self):
        return self.create_with(lambda taccount: taccount.condense())

    # TODO test this
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


# FIXME: добавить класс TrialBalanceViewer
class TrialBalance(UserDict[str, tuple[int, int]]):
    # xopowen
    # возможноли в будущем увиличение количчества column ?
    # что они должны показыват? стоит изменить имена
    # EP: нужно буджет перенести в TrialBalanceViewer

    def account_names_column(self):
        names = [
            name.replace("_", " ").strip().capitalize() for name in self.data.keys()
        ]
        return Column(names).align_left(".").add_space(1).header("Account")

    def debit_column(self):
        return (
            Column([str(d) for (d, _) in self.data.values()])
            .align_right()
            .add_space_left(2)
            .header("Debit")
            .add_space(2)
        )

    def credit_column(self):
        return (
            Column([str(c) for (_, c) in self.data.values()])
            .align_right()
            .add_space_left(2)
            .header("Credit")
        )

    def table(self):
        return self.account_names_column() + self.debit_column() + self.credit_column()

    def view(self):
        return self.table().printable()


##эту фозможно стоить прекрепить к классу связаному по смыслу как  staticmethod
# xopowen
# EP: по сути да, иногда я спицально откреплял, чтобы self, не маячил
#     возможно для читаемости нужно к классу ledger прикрепить
def yield_tuples(ledger):
    for name, taccount in ledger.subset(accounts.DebitAccount).data.items():
        yield name, taccount.balance(), 0
    for name, taccount in ledger.subset(accounts.CreditAccount).data.items():
        yield name, 0, taccount.balance()


##эту фозможно стоить прекрепить к классу связаному по смыслу как  staticmethod
# xopowen
def trial_balance(chart, ledger):
    ignore = [chart.null_account, chart.income_summary_account]
    return TrialBalance(
        {name: (a, b) for name, a, b in yield_tuples(ledger) if name not in ignore}
    )


# xopowen
# лично мне этот класс нравится больше всех. локаничный
@dataclass
class Reporter:
    chart: BaseChart
    ledger: BaseLedger
    titles: dict[str, str] = field(default_factory=dict)

    @property
    def pipeline(self):
        return Pipeline(self.chart, self.ledger)

    def income_statement(self, header="Income Statement"):
        # есть ли смысл создавать дополнителную ссылку ?
        # EP: допольнительную переменную p? я хочу показать p отличается в разных методах
        #     намерение такое было
        # xopowen
        p = self.pipeline.close_first()
        return p.ledger.income_statement().viewer(self.titles, header)

    def balance_sheet(self, header="Balance Sheet"):
        p = self.pipeline.close_first().close_second().close_last()
        return p.ledger.balance_sheet().viewer(self.titles, header)

    # xopowen
    # возможно не дописана ЕП:++
    # отрефакторю как TrialBalanceViewer будет
    def trial_balance(self, header="Trial Balance"):
        return trial_balance(self.chart, self.ledger)
