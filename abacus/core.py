"""Core elements of a minimal double-entry accounting system.

Using this module you can:

- create a chart of accounts using `Chart` class,
- create `Ledger` from `Chart`,
- post entries to `Ledger`,
- generate trial balance, balance sheet and income statement.

Implemented in this module:

- **contra accounts** — there can be a `refunds` account that offsets `income:sales`
  and `depreciation` account that offsets `asset:ppe`,
- **multiple entries** — debit and credit several accounts in one transaction,
- **closing entries** — proper closing of accounts at the accounting period end.

Assumptions and simplifications:

1. no sub-accounts — there is only one level of account hierarchy in chart
2. account names must be globally unique
3. no cashflow statement
4. one currency
5. no checks for account non-negativity
"""

import json
from abc import ABC, abstractmethod
from collections import UserDict
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import ClassVar, Iterable, Type

__all__ = [
    "AbacusError",
    "Amount",
    "Chart",
    "Entry",
    "T",
    "TrialBalance",
    "Ledger",
    "BalanceSheet",
    "IncomeStatement",
    "AccountBalances",
    "Pipeline",
]


class AbacusError(Exception):
    """Custom error for this project."""


# FIXME: can use decimal.Decimal
Amount = int


class T(Enum):
    """Five types of accounts and standard prefixes for account names."""

    Asset = "asset"
    Liability = "liability"
    Capital = "capital"
    Income = "income"
    Expense = "expense"


class Holder(ABC):
    """The `Holder` class is a wrapper to hold an account type
       that would be convertible to T-account.

    Child classes are:

    - `Regular(Holder)` for regular accounts,
    - `Contra(Holder)` for contra accounts,
    - `Wrap(Holder)` for income summary and null account.

    This wrapping enables to pattern match on account type
    and make type conversions cleaner.
    """

    @property
    @abstractmethod
    def t_account(
        self,
    ) -> type["RegularAccount"] | type["ContraAccount"] | type["ExtraAccount"]:
        # Type["TAccount"]:
        # type["RegularAccount"] | type["ContraAccount"] | type["ExtraAccount"]:
        """Provide T-account constructor."""


@dataclass
class Regular(Holder):
    t: T

    @property
    def t_account(self) -> type["RegularAccount"]:
        match self:
            case Regular(T.Asset):
                return Asset
            case Regular(T.Capital):
                return Capital
            case Regular(T.Liability):
                return Liability
            case Regular(T.Income):
                return Income
            case Regular(T.Expense):
                return Expense
            case _:
                raise ValueError(f"Invalid type: {self}")


@dataclass
class Contra(Holder):
    t: T

    @property
    def t_account(self) -> Type["ContraAccount"]:
        match self:
            case Contra(T.Asset):
                return ContraAsset
            case Contra(T.Capital):
                return ContraCapital
            case Contra(T.Liability):
                return ContraLiability
            case Contra(T.Income):
                return ContraIncome
            case Contra(T.Expense):
                return ContraExpense
            case _:
                raise ValueError(f"Invalid type: {self}")


@dataclass
class Account:
    name: str
    contra_accounts: list[str] = field(default_factory=list)

    @staticmethod
    def from_string(s) -> "Account":
        if isinstance(s, str):
            return Account(s, [])
        return s

    def __str__(self):
        return self.name


@dataclass
class TAccount(ABC):
    """T-account will hold amounts on debits and credit side."""

    debits: list[Amount] = field(default_factory=list)
    credits: list[Amount] = field(default_factory=list)

    def debit(self, amount: Amount):
        """Add debit amount to account."""
        self.debits.append(amount)

    def credit(self, amount: Amount):
        """Add credit amount to account."""
        self.credits.append(amount)

    @abstractmethod
    def balance(self) -> Amount:
        """Return account balance."""

    @abstractmethod
    def transfer_balance(self, my_name: str, dest_name: str) -> "Entry":
        """Create an entry that transfers account balance from this account
        to destination account.

        This account name is `my_name` and destination account name is `dest_name`.
        """

    def condense(self):
        """Create a new account of the same type with only one value as account balance."""
        return self.empty().topup(self.balance())

    def empty(self):
        """Create a new empty account of the same type."""
        return self.__class__()

    def topup(self, balance):
        """Add starting balance to a proper side of account."""
        match self:
            case DebitAccount(_, _):
                self.debit(balance)
            case CreditAccount(_, _):
                self.credit(balance)
        return self


class DebitAccount(TAccount):
    def balance(self):
        return sum(self.debits) - sum(self.credits)

    def transfer_balance(self, my_name: str, dest_name: str) -> "Entry":
        return Entry(debit=dest_name, credit=my_name, amount=self.balance())


class CreditAccount(TAccount):
    def balance(self):
        return sum(self.credits) - sum(self.debits)

    def transfer_balance(self, my_name: str, dest_name: str) -> "Entry":
        return Entry(debit=my_name, credit=dest_name, amount=self.balance())


class RegularAccount: ...


class Asset(RegularAccount, DebitAccount): ...


class Capital(RegularAccount, CreditAccount): ...


class Liability(RegularAccount, CreditAccount): ...


class Income(RegularAccount, CreditAccount): ...


class Expense(RegularAccount, DebitAccount): ...


class ContraAccount: ...


class ContraAsset(ContraAccount, CreditAccount): ...


class ContraCapital(ContraAccount, DebitAccount): ...


class ContraLiability(ContraAccount, DebitAccount): ...


class ContraIncome(ContraAccount, DebitAccount): ...


class ContraExpense(ContraAccount, CreditAccount): ...


class ExtraAccount: ...


class ExtraCreditAccount(ExtraAccount, CreditAccount): ...


class IncomeSummaryAccount(ExtraCreditAccount): ...


class NullAccount(ExtraCreditAccount): ...


class ExtraDebitAccount(ExtraAccount, DebitAccount): ...


@dataclass
class Wrap(Holder):
    """Holder for accounts that do not belong to any of 5 account types.

    There are two temporary accounts where this holder is needed:

       - income summary account,
       - null account.

    Note: Income summary account should have zero balance at the end of accounting period.
    Null account should always has zero balance.
    """

    t: type[ExtraAccount]

    @property
    def t_account(self) -> type[ExtraAccount]:
        return self.t


@dataclass
class Chart:
    """Chart of accounts.

    Example:

    ```python
    chart = Chart(assets=["cash"], capital=["equity"])
    ```
    """

    income_summary_account: str = "_isa"
    retained_earnings_account: str = "retained_earnings"
    null_account: str = "_null"
    assets: list[str | Account] = field(default_factory=list)
    capital: list[str | Account] = field(default_factory=list)
    liabilities: list[str | Account] = field(default_factory=list)
    income: list[str | Account] = field(default_factory=list)
    expenses: list[str | Account] = field(default_factory=list)

    def __post_init__(self):
        self.validate()

    def validate(self) -> "Chart":
        a = list(self.to_dict().keys())
        b = [x[0] for x in self.dict_items()]
        if len(a) != len(b):
            raise AbacusError(
                [
                    "Chart should not contain duplicate account names.",
                    len(a),
                    len(b),
                    set(b) - set(a),
                ]
            )
        return self

    def to_dict(self) -> dict[str, Holder]:
        """Return a dictionary of account names and account types.
        Will purge duplicate names if found in chart.
        """
        return dict(self.dict_items())

    def dict_items(self):
        """Assign account types to account names."""
        yield from self.stream(self.assets, T.Asset)
        yield from self.stream(self.capital, T.Capital)
        yield self.retained_earnings_account, Regular(T.Capital)
        yield from self.stream(self.liabilities, T.Liability)
        yield from self.stream(self.income, T.Income)
        yield from self.stream(self.expenses, T.Expense)
        yield self.income_summary_account, Wrap(IncomeSummaryAccount)
        yield self.null_account, Wrap(NullAccount)

    def pure_accounts(self, xs: list[str | Account]) -> list[Account]:
        return [Account.from_string(x) for x in xs]

    def stream(self, items, t: T):
        for account in self.pure_accounts(items):
            yield account.name, Regular(t)
            for contra_name in account.contra_accounts:
                yield contra_name, Contra(t)

    def ledger(self, starting_balances: dict | None = None):
        return Ledger.new(self, AccountBalances(starting_balances))


@dataclass
class Entry:
    """Double entry with account name to be debited,
       account name to be credited and transaction amount.

    Example:

    ```python
    entry = Entry(debit="cash", credit="equity", amount=20000)
    ```
    """

    debit: str
    credit: str
    amount: Amount

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_string(cls, line: str):
        return cls(**json.loads(line))


class AccountBalances(UserDict[str, Amount]):
    def nonzero(self):
        return self.__class__(
            {name: balance for name, balance in self.items() if balance}
        )

    def total(self):
        return sum(self.values())

    def json(self):
        return json.dumps(self.data, indent=4, ensure_ascii=False)

    def save(self, path: Path | str):
        Path(path).write_text(self.json(), encoding="utf-8")

    @classmethod
    def load(cls, path: Path | str):
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))


def starting_entries(chart: Chart, balances: AccountBalances):
    return CompoundEntry.from_balances(chart, balances).to_entries(chart.null_account)


class Ledger(UserDict[str, TAccount]):
    @classmethod
    def new(cls, chart: Chart, balances: AccountBalances | None):
        """Create a new ledger from chart, possibly using starting balances."""
        ledger = cls({name: h.t_account() for name, h in chart.dict_items()})  # type: ignore
        if balances:
            entries = starting_entries(chart, balances)
            ledger.post_many(entries)
        return ledger

    def post(self, debit: str, credit: str, amount: Amount, title: str = ""):
        """Post to ledger using debit and credit account names and amount."""
        # FIXME: title is discarded
        return self.post_one(Entry(debit, credit, amount))

    def post_one(self, entry: Entry):
        """Post one double entry to ledger."""
        return self.post_many(entries=[entry])

    def post_many(self, entries: Iterable[Entry]):
        """Post several double entries to ledger."""
        failed = []
        for entry in entries:
            try:
                self.data[entry.debit].debit(amount=entry.amount)
                self.data[entry.credit].credit(amount=entry.amount)
            except KeyError:
                failed.append(entry)
        if failed:
            raise AbacusError(failed)
        return self

    @property
    def balances(self):
        """Return account balances."""
        return AccountBalances(
            {name: account.balance() for name, account in self.items()}
        )

    def subset(self, cls: Type[TAccount]):
        """Filter ledger by account type."""
        return self.__class__(
            {
                account_name: t_account
                for account_name, t_account in self.data.items()
                if isinstance(t_account, cls)
            }
        )

    def condense(self):
        """Return a new ledger with condensed accounts that hold just one value.
        Used to avoid copying of ledger data where only account balances are needed."""
        return self.__class__(
            {name: account.condense() for name, account in self.items()}
        )


def contra_pairs(chart: Chart, contra_t: Type[ContraAccount]) -> list[tuple[str, str]]:
    """Return list of account and contra account name pairs for a given type of contra account."""
    attr = {
        "ContraAsset": "assets",
        "ContraLiability": "liabilities",
        "ContraCapital": "capital",
        "ContraExpense": "expenses",
        "ContraIncome": "income",
    }[contra_t.__name__]
    regular_accounts = chart.pure_accounts(getattr(chart, attr))
    return [
        (account.name, contra_name)
        for account in regular_accounts
        for contra_name in account.contra_accounts
    ]


class Pipeline:
    """A pipeline to accumulate ledger transformations."""

    def __init__(self, chart: Chart, ledger: Ledger):
        self.chart = chart
        self.ledger = deepcopy(ledger)
        self.closing_entries: list[Entry] = []

    def append_and_post(self, entry: Entry):
        self.ledger.post_one(entry)
        self.closing_entries.append(entry)

    def close_contra(self, t: Type[ContraAccount]):
        """Close contra accounts of type `t`."""
        for account, contra_account in contra_pairs(self.chart, t):
            entry = self.ledger.data[contra_account].transfer_balance(
                contra_account, account
            )
            self.append_and_post(entry)
        return self

    def close_to_isa(self):
        """Close income or expense accounts to income summary account."""
        for name, account in self.ledger.data.items():
            if isinstance(account, Income) or isinstance(account, Expense):
                entry = account.transfer_balance(
                    name, self.chart.income_summary_account
                )
                self.append_and_post(entry)
        return self

    def close_isa_to_re(self):
        """Close income summary account to retained earnings account."""
        entry = Entry(
            debit=self.chart.income_summary_account,
            credit=self.chart.retained_earnings_account,
            amount=self.ledger.data[self.chart.income_summary_account].balance(),
        )
        self.append_and_post(entry)
        return self

    def close_first(self):
        """Close contra income and contra expense accounts."""
        self.close_contra(ContraIncome)
        self.close_contra(ContraExpense)
        return self

    def close_second(self):
        """Close income and expense accounts to income summary account,
        then close income summary account to retained earnings."""
        self.close_to_isa()
        self.close_isa_to_re()
        return self

    def close_last(self):
        """Close permanent contra accounts."""
        self.close_contra(ContraAsset)
        self.close_contra(ContraLiability)
        self.close_contra(ContraCapital)
        return self

    def close(self):
        self.close_first()
        self.close_second()
        self.close_last()
        return self


@dataclass
class Report:
    chart: Chart
    ledger: Ledger
    rename_dict: dict[str, str] = field(default_factory=dict)

    # FIXME: may condense chart after init

    def rename(self, key, value):
        self.rename_dict[key] = value
        return self

    @property
    def pipeline(self):
        return Pipeline(self.chart, self.ledger)

    @property
    def balance_sheet(self):
        p = self.pipeline.close_first().close_second().close_last()
        return BalanceSheet.new(p.ledger)

    @property
    def balance_sheet_before_closing(self):
        return BalanceSheet.new(self.ledger)

    @property
    def income_statement(self):
        p = self.pipeline.close_first()
        return IncomeStatement.new(p.ledger)

    @property
    def trial_balance(self):
        return TrialBalance.new(self.ledger)

    @property
    def account_balances(self):
        return self.ledger.balances

    def print_all(self):
        from abacus.viewers import print_viewers

        tv = self.trial_balance.viewer
        bv = self.balance_sheet.viewer
        iv = self.income_statement.viewer
        print_viewers(self.rename_dict, tv, bv, iv)


class Statement(ABC):
    @property
    @abstractmethod
    def viewer(self): ...

    def __str__(self):
        return str(self.viewer)

    def print(self, width=None):
        return self.viewer.print(width)


@dataclass
class BalanceSheet(Statement):
    assets: AccountBalances
    capital: AccountBalances
    liabilities: AccountBalances

    @property
    def viewer(self):
        from abacus.viewers import BalanceSheetViewer

        return BalanceSheetViewer(self)

    @classmethod
    def new(cls, ledger: Ledger):
        return cls(
            assets=ledger.subset(Asset).balances,
            capital=ledger.subset(Capital).balances,
            liabilities=ledger.subset(Liability).balances,
        )


@dataclass
class IncomeStatement(Statement):
    income: AccountBalances
    expenses: AccountBalances
    default_header: ClassVar[str] = "Income statement"

    @property
    def viewer(self):
        from abacus.viewers import IncomeStatementViewer

        return IncomeStatementViewer(self)

    @classmethod
    def new(cls, ledger: Ledger):
        return cls(
            income=ledger.subset(Income).balances,
            expenses=ledger.subset(Expense).balances,
        )

    def current_profit(self):
        return sum(self.income.values()) - sum(self.expenses.values())


class TrialBalance(UserDict[str, tuple[Amount, Amount]], Statement):
    """Trial balance is a dictionary of account names and
    their debit-side and credit-side balances."""

    @classmethod
    def new(cls, ledger: Ledger):
        _ledger = ledger.condense()
        tb = cls()
        for name, balance in _ledger.subset(DebitAccount).balances.items():
            tb[name] = (balance, 0)
        for name, balance in _ledger.subset(CreditAccount).balances.items():
            tb[name] = (0, balance)
        return cls(tb)

    @property
    def viewer(self):
        from abacus.viewers import TrialBalanceViewer

        return TrialBalanceViewer(self.data)


def sum_second(xs):
    return sum(x for _, x in xs)


@dataclass
class CompoundEntry:
    """An entry that affects several accounts at once."""

    debits: list[tuple[str, Amount]]
    credits: list[tuple[str, Amount]]

    def __post_init__(self):
        self.validate()

    def validate(self):
        """Assert sum of debit entries equals sum of credit entries."""
        if sum_second(self.debits) == sum_second(self.credits):
            return self
        else:
            raise AbacusError(["Invalid multiple entry", self])

    def to_entries(self, null_account_name: str) -> list[Entry]:
        """Return list of double entries that make up multiple entry.
        The double entries will correspond to null account.
        """
        a = [
            Entry(account_name, null_account_name, amount)
            for (account_name, amount) in self.debits
        ]
        b = [
            Entry(null_account_name, account_name, amount)
            for (account_name, amount) in self.credits
        ]
        return a + b

    @classmethod
    def from_balances(cls, chart: Chart, balances: AccountBalances) -> "CompoundEntry":
        ledger = chart.ledger()

        def is_debit(name):
            return isinstance(ledger.data[name], DebitAccount)

        def is_credit(name):
            return isinstance(ledger.data[name], CreditAccount)

        return cls(
            debits=[(name, b) for name, b in balances.items() if is_debit(name)],
            credits=[(name, b) for name, b in balances.items() if is_credit(name)],
        )
