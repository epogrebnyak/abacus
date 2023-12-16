from dataclasses import dataclass, field
from typing import Callable, Iterable, Type

from pydantic import BaseModel

import abacus.engine.accounts as accounts  # type: ignore
from abacus.engine.accounts import ContraAccount  # type: ignore
from abacus.engine.accounts import AbacusError, Entry, TAccount


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
    income_summary: str = "income_summary_account"
    retained_earnings: str = "re"
    null: str = "null"

    def as_string(self, label: Label | Offset) -> str:
        return label.as_string(prefix(self, label))

    def extract(self, label_string: str) -> Label | Offset:
        match label_string.strip().lower().split(":"):
            case [prefix, name]:
                return label_class(self, prefix)(name)
            case [self.contra, account_name, contra_account_name]:
                return Offset(contra_account_name, account_name)
            case _:
                raise ValueError(f"Invalid label: {label_string}.")


def prefix(composer: Composer, label: Label | Offset) -> str:
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
        case IncomeSummaryLabel(_):
            return composer.income_summary
        case RetainedEarningsLabel(_):
            return composer.retained_earnings
        case NullLabel(_):
            return composer.null
        case Offset(_, _):
            return composer.contra
        case _:
            raise ValueError(f"Invalid label: {label}.")


def label_class(composer: Composer, prefix: str) -> Type[Label | Offset]:
    """Return label or offset class contructor given the prefix string."""
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
        case composer.income_summary:
            return IncomeSummaryLabel
        case composer.retained_earnings:
            return RetainedEarningsLabel
        case composer.null:
            return NullLabel
        case _:
            raise ValueError(f"Invalid label: {prefix}.")


@dataclass
class ChartList:
    accounts: list[Label | Offset]

    def names(self):
        return [account.name for account in self.accounts]

    @property
    def labels(self):
        return [account for account in self.accounts if isinstance(account, Label)]

    @property
    def offsets(self):
        return [account for account in self.accounts if isinstance(account, Offset)]

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

    def add_many(self, *label_strings: list[str], composer=Composer()):
        for s in label_strings:
            self.add(s, composer)
        return self

    def filter(self, cls: Type[Label] | Type[Offset]):
        return [account for account in self.accounts if isinstance(account, cls)]

    def filter_name(self, cls: Type[Label]):
        return [account.name for account in self.accounts if isinstance(account, cls)]

    @property
    def income_summary_account(self):
        return self._get_exactly_one(IncomeSummaryLabel)

    @property
    def retained_earnings_account(self):
        return self._get_exactly_one(RetainedEarningsLabel)

    @property
    def null_account(self):
        return self._get_exactly_one(NullLabel)

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

    def _find_offsets(self, name: str):
        return [offset for offset in self.filter(Offset) if offset.offsets == name]

    def _get_exactly_one(self, cls: Type[Label]):
        matches = self.filter(cls)
        match len(matches):
            case 1:
                return matches[0].name
            case _:
                raise ValueError(
                    f"Expected exactly one {cls.__name__}, found {len(matches)}."
                )

    def stream(self, label_class, account_class, contra_account_class):
        """Yield tuples of account names and account or contra account classes."""
        for label in self.filter(label_class):
            yield label.name, account_class
            for offset in self._find_offsets(label.name):
                yield offset.name, contra_account_class

    def t_accounts(self):
        yield from self.stream(AssetLabel, accounts.Asset, accounts.ContraAsset)
        yield from self.stream(CapitalLabel, accounts.Capital, accounts.ContraCapital)
        yield from self.stream(
            LiabilityLabel, accounts.Liability, accounts.ContraLiability
        )
        yield from self.stream(IncomeLabel, accounts.Income, accounts.ContraIncome)
        yield from self.stream(ExpenseLabel, accounts.Expense, accounts.ContraExpense)
        yield self._get_exactly_one(IncomeSummaryLabel), accounts.IncomeSummaryAccount
        yield self._get_exactly_one(RetainedEarningsLabel), accounts.RetainedEarnings
        yield self._get_exactly_one(NullLabel), accounts.NullAccount

    def ledger_dict(self):
        return {name: t_account() for name, t_account in self.t_accounts()}

    def ledger(self):
        return BaseLedger(self.ledger_dict())

    def contra_pairs(self, cls: Type[ContraAccount]) -> list[Offset]:
        klass = {
            "ContraAsset": AssetLabel,
            "ContraLiability": LiabilityLabel,
            "ContraCapital": CapitalLabel,
            "ContraExpense": ExpenseLabel,
            "ContraIncome": IncomeLabel,
        }[cls.__name__]
        return [
            offset
            for label in self.filter(klass)
            for offset in self._find_offsets(label.name)
        ]

    def __getitem__(self, name: str) -> Label | Offset:
        return {account.name: account for account in self.accounts}[name]


def base_chart_list():
    return ChartList(
        [
            IncomeSummaryLabel("current_profit"),
            RetainedEarningsLabel("retained_earnings"),
            NullLabel("null"),
        ]
    )


def make_chart(*strings: list[str]):
    return base_chart_list().add_many(*strings)


x = make_chart("asset:cash", "capital:equity", "contra:equity:ts")
print(x)
print(x["ts"] == [Offset("ts", "equity")])
print(x["ts"].as_string("contra") == "contra:equity:ts")
print(
    x.names() == ["current_profit", "retained_earnings", "null", "cash", "equity", "ts"]
)
print(
    ChartList(x.labels).names()
    == ["current_profit", "retained_earnings", "null", "cash", "equity"]
)
print(ChartList(x.offsets).names() == ["ts"])
print(
    x.ledger_dict().keys()
    == {"current_profit", "retained_earnings", "null", "cash", "equity", "ts"}
)
print(x.contra_pairs(accounts.ContraCapital) == [Offset("ts", "equity")])


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

    def apply(self, f: Callable):
        self.data = {name: f(taccount) for name, taccount in self.data.items()}
        return self

    def deep_copy(self):
        return self.apply(lambda taccount: taccount.deep_copy())

    def condense(self):
        return self.apply(lambda taccount: taccount.condense())

    def balances(self):
        return self.apply(lambda taccount: taccount.balance()).data

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
    for offset in chart.contra_pairs(contra_cls):
        yield ledger.data[offset.name].transfer(offset.name, offset.offsets)  # type: ignore


x.add_many("income:sales", "contra:sales:refunds", "expense:salaries")
ledger = x.ledger()
ledger.post("cash", "equity", 12_000)
ledger.post("ts", "cash", 2_000)
ledger.post("cash", "sales", 3_499)
ledger.post("refunds", "cash", 499)
ledger.post("salaries", "cash", 2_001)
assert list(closing_contra_entries(x, ledger, accounts.ContraCapital)) == [
    Entry(debit="equity", credit="ts", amount=2000)
]
assert list(closing_contra_entries(x, ledger, accounts.ContraIncome)) == [
    Entry(debit="sales", credit="refunds", amount=499)
]


def close_to_income_summary_account(chart, ledger, cls):
    for name, account in ledger.data.items():
        if isinstance(account, cls):
            yield account.transfer(name, chart.income_summary_account)


def close_first(chart, ledger):
    """Close contra income and contra expense accounts."""
    c1 = closing_contra_entries(chart, ledger, accounts.ContraIncome)
    c2 = closing_contra_entries(chart, ledger, accounts.ContraExpense)
    closing_entries = list(c1) + list(c2)
    return ledger.post_many(closing_entries), closing_entries


def close_second(chart, dummy_ledger):
    """Close income and expense accounts to income summary account ("income_summary_account"),
    then close income_summary_account to retained earnings."""
    # Close income and expense to income_summary_account
    a = close_to_income_summary_account(chart, dummy_ledger, accounts.Income)
    b = close_to_income_summary_account(chart, dummy_ledger, accounts.Expense)
    closing_entries = list(a) + list(b)
    dummy_ledger.post_many(closing_entries)
    # Close income_summary_account to retained earnings
    income_summary_account, re = (
        chart.income_summary_account,
        chart.retained_earnings_account,
    )
    b = dummy_ledger.data[income_summary_account].balance()
    transfer_entry = Entry(debit=income_summary_account, credit=re, amount=b)
    closing_entries.append(transfer_entry)
    return dummy_ledger.post_many(closing_entries), closing_entries


def close_last(chart, ledger):
    """Close permanent contra accounts."""
    c3 = closing_contra_entries(chart, ledger, accounts.ContraAsset)
    c4 = closing_contra_entries(chart, ledger, accounts.ContraLiability)
    c5 = closing_contra_entries(chart, ledger, accounts.ContraCapital)
    closing_entries = list(c3) + list(c4) + list(c5)
    return ledger.post_many(closing_entries), closing_entries


def chain(chart, ledger, functions):
    _ledger = ledger.condense().deep_copy()
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


class _TrialBalance(BaseModel):
    lines: list[tuple[str, int, int]]


def make_trial_balance(chart, ledger):
    return _TrialBalance(lines=list(yield_tuples_for_trial_balance(chart, ledger)))


@dataclass
class Reporter:
    chart: ChartList
    ledger: BaseLedger
    titles: dict[str, str] = field(default_factory=dict)

    def income_statement(self, header="Income Statement"):
        from abacus.engine.report import IncomeStatement, IncomeStatementViewer

        ledger, _ = chain(self.chart, self.ledger, [close_first])
        print("closing entries", _)
        print(ledger.data["salaries"])
        statement = IncomeStatement.new(ledger)
        return IncomeStatementViewer(statement, self.titles, header)

    def balance_sheet(self, header="Balance Sheet"):
        from abacus.engine.report import BalanceSheet, BalanceSheetViewer

        ledger, _ = chain(
            self.chart, self.ledger, [close_first, close_second, close_last]
        )
        print(_)
        print(ledger.data["salaries"])
        statement = BalanceSheet.new(ledger)
        return BalanceSheetViewer(statement, self.titles, header)

    def trial_balance(self, header="Trial Balance"):
        # ledger, _ = chain(self.chart, self.ledger, [])
        print(ledger.data["salaries"])
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


from abacus.engine.report import Column


def nth(data, n: int, f=str) -> Column:
    """Make a column from nth element of each tuple or list in `data`."""
    return Column([f(d[n]) for d in data])


r = Reporter(x, ledger)
print(r.tb())
# income statement and balance sheet corrupt initial ledger!
print(r.income_statement())
print(r.balance_sheet())
print(r.trial_balance())
print(r.tb())
