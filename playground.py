"""Accounting module for double-entry bookkeeping.

add assumptions from issue 80 
and:
- account is always either debit side or credit side
- no journals, entries get poted to ledger directly
- how closing is made
- net earnings made of income and expenses, no gross profit or profit before tax   
"""

import decimal
from abc import ABC, abstractmethod
from collections import UserDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class AbacusError(Exception):
    """Custom error for the abacus project."""


AccountName = str

class Amount(decimal.Decimal):

    def entry(self, debit, credit):
        return DoubleEntry(amount=self, debit=debit, credit=credit)


class Side(Enum):
    """Indicate debit (right) or credit (left) side of the account."""

    Debit = "debit"
    Credit = "credit"

    def reverse(self) -> "Side":
        """Change side from debit to credit and vice versa."""
        if self == Side.Debit:
            return Side.Credit
        return Side.Debit

    def __repr__(self):
        """Make this enum look better in messages."""
        return str(self)


class T5(Enum):
    """Five types of accounts."""

    Asset = "asset"
    Liability = "liability"
    Capital = "capital"
    Income = "income"
    Expense = "expense"

    @staticmethod
    def which(t: "T5") -> Side:
        """Associate each type of account with debit or credit side."""
        if t in [T5.Asset, T5.Expense]:
            return Side.Debit
        return Side.Credit


class Holder(ABC):
    """Abstract class for construction regular, contra or intermediate accounts.
    
    Examples:
        Regular(T5.Asset)
        Contra(T5.Income)
        Intermediate(Profit.IncomeSummaryAccount)

    Regular and Contra constructors help to define each of five account types
    and their contra accounts. Intermediate constructor used for profit accounts, 
    that live a short while after closing entries.
    """

    @property
    @abstractmethod
    def side(self) -> Side:
        """Indicate side of account (debit or credit)."""
        pass

    def taccount(self):
        """Create T-account for this account definition."""
        return TAccount(self.side)


@dataclass
class Regular(Holder):
    """Regular accounts of five types."""
    t: T5

    @property
    def side(self) -> Side:
        return T5.which(self.t)


@dataclass
class Contra(Holder):
    """A contra account to any of five types of account. 
    
    Examples of contra accounts (generated text below):
        - contra property, plant, equipment account: accumulated depreciation
        - contra liability account: discount on bonds payable (?)
        - contra capital account: treasury stock
        - contra income account: refunds 
        - contra expense account: purchase discounts
    """
    t: T5

    @property
    def side(self) -> Side:
        return T5.which(self.t).reverse()


class Profit(Enum):
    IncomeSummaryAccount = "isa"
    OtherComprehensiveIncome = "oci" # not implemented yet


@dataclass
class Intermediate(Holder):
    """Intermediate account used for profit accounts only."""
    t: Profit

    @property
    def side(self) -> Side:
        if isinstance(self.t, Profit):
            return Side.Credit
        raise AbacusError("Unknown intermediate account: " + str(self.t))


@dataclass
class SingleEntry:
    """Single entry for the ledger."""

    account_name: AccountName
    amount: Amount
    # maybe add UUID for entry identification


def amounts(xs: Iterable[SingleEntry]) -> Amount:
    """Sum amounts in a list of single entries."""
    return Amount(sum(x.amount for x in xs))


@dataclass
class MultipleEntry:
    debit: list[SingleEntry]
    credit: list[SingleEntry]

    def __post_init__(self):
        if not amounts(self.debit) == amounts(self.credit):
            raise AbacusError(
                "Debits and credits are not equal in this entry: " + str(self)
            )
            

def DoubleEntry(debit, credit, amount) -> MultipleEntry:
    """Create double entry from debit account name, credit account name and entry amount.
    
    Note that Entry is a function that returns MultipleEntry, it is not a class itself.
    This naming is a small trick."""
    return MultipleEntry(
        debit=[SingleEntry(debit, amount)],
        credit=[SingleEntry(credit, amount)],
    )


@dataclass
class Account:
    """Account definition with contra accounts."""
    name: AccountName
    contra_accounts: list[AccountName] = field(default_factory=list)


@dataclass
class Chart:
    """Chart of accounts.

    Example:

    ```python
    chart = Chart(assets=[Account("cash")], capital=[Account("equity")])
    ```
    """

    income_summary_account: str = "isa"
    retained_earnings_account: str = "retained_earnings"
    assets: list[Account] = field(default_factory=list)
    capital: list[Account] = field(default_factory=list)
    liabilities: list[Account] = field(default_factory=list)
    income: list[Account] = field(default_factory=list)
    expenses: list[Account] = field(default_factory=list)

    def dict(self):
        return dict(self.items())

    def items(self):
        """Assign account types to account names."""
        yield from self.stream(self.assets, T5.Asset)
        yield from self.stream(self.capital, T5.Capital)
        yield self.retained_earnings_account, Regular(T5.Capital)
        yield from self.stream(self.liabilities, T5.Liability)
        yield from self.stream(self.income, T5.Income)
        yield from self.stream(self.expenses, T5.Expense)
        yield self.income_summary_account, Intermediate(Profit.IncomeSummaryAccount)

    @staticmethod
    def stream(accounts: list[Account], account_type: T5):
        for account in accounts:
            yield account.name, Regular(account_type)
            for contra_name in account.contra_accounts:
                yield contra_name, Contra(account_type)

    def __post_init__(self):
        a = list(self.dict().keys())
        b = [x[0] for x in self.items()]
        if len(a) != len(b):
            raise AbacusError(
                [
                    "Chart should not contain duplicate account names.",
                    len(b) - len(a),
                    set(b) - set(a),
                ]
            )


@dataclass
class TAccount:
    """T-account holds amounts on debit and credit side."""

    side: Side
    debits: list[Amount] = field(default_factory=list)
    credits: list[Amount] = field(default_factory=list)

    def debit(self, amount: Amount):
        """Add debit amount to account."""
        self.debits.append(amount)

    def credit(self, amount: Amount):
        """Add credit amount to account."""
        self.credits.append(amount)

    def _is_debit_account(self) -> bool:
        """Return True if this account is debit account."""
        return self.side == Side.Debit

    def balance(self) -> Amount:
        """Return account balance."""
        b = Amount(sum(self.debits) - sum(self.credits))
        return b if self._is_debit_account() else -b


class Ledger(UserDict[AccountName, TAccount]):
    @classmethod
    def new(cls, chart: Chart):
        """Create new ledger from chart of accounts."""
        return cls({name: definition.taccount() for name, definition in chart.items()})

    def post_one(self, entry: MultipleEntry):
        """Post one multiple entry to ledger."""
        return self.post_many([entry])

    def post_many(self, entries: Iterable[MultipleEntry]):
        """Post several multiple entries to ledger."""
        failed = []
        for entry in entries:
            try:
                for debit in entry.debit:
                    self.data[debit.account_name].debit(amount=debit.amount)
                for credit in entry.credit:
                    self.data[credit.account_name].credit(amount=credit.amount)
            except KeyError:
                failed.append(entry)
        if failed:
            raise AbacusError(["Could not post to ledger:", failed])
        return self
    
    def trial_balance(self):
        return TrialBalance.new(self)


class TrialBalance(UserDict[str, tuple[Side, Amount]]):

    @classmethod 
    def new(cls, ledger: Ledger):
        return cls(            
        {
        account_name: (t_account.side, t_account.balance())
        for account_name, t_account in ledger.items()
        }
        )
    
    def tuples(self):        
        def to_tuples(side, balance):
            if side == Side.Debit:
                return balance, 0
            else:
                return 0, balance
        return {name: to_tuples(side, balance) for name, (side, balance) in self.items()}

    def balances(self):
        return {name: balance for name, (_, balance) in self.items()}



@dataclass
class IncomeSummary:
    income: dict[AccountName, Amount] = field(default_factory=dict)
    expenses: dict[AccountName, Amount] = field(default_factory=dict)

    def net_earnings(self):
        return sum(self.income.values()) - sum(self.expenses.values())



def close(ledger: Ledger, chart: Chart):
    """Close ledger at accounting period end following these steps:
       - close income and expense contra accounts,
       - close income and expense accounts to income summary account,
       - close income summary account to retained earnings.
    """
    isa = chart.income_summary_account
    re = chart.retained_earnings_account
    closing_entries = []
    # Close contra_accounts
    for account in chart.income:
        for a in account.contra_accounts:
            e = DoubleEntry(debit=account.name, credit=a, amount=ledger[a].balance())
            closing_entries.append(e)
            ledger.post_one(e)
            del ledger[a]
    for account in chart.expenses:
        for a in account.contra_accounts:
            e = DoubleEntry(debit=a, credit=account.name, amount=ledger[a].balance())
            closing_entries.append(e)
            ledger.post_one(e)
            del ledger[a]
    income_summary = IncomeSummary()
    # Close income and expense accounts
    for account in chart.income:
        a = account.name
        b = ledger[a].balance()
        income_summary.income[a] = b
        e = DoubleEntry(debit=a, credit=isa, amount=b)
        closing_entries.append(e)
        ledger.post_one(e)
        del ledger[a]
    for account in chart.expenses:
        a = account.name
        b = ledger[a].balance()
        income_summary.expenses[a] = b
        e = DoubleEntry(debit=isa, credit=a, amount=b)
        closing_entries.append(e)
        ledger.post_one(e)
        del ledger[a]
    # Close to retained earnings
    e = DoubleEntry(debit=isa, credit=re, amount=ledger[isa].balance())
    closing_entries.append(e)
    ledger.post_one(e)
    del ledger[isa]
    # note we actually mutate the ledger
    return closing_entries, ledger, income_summary

entries = [
    DoubleEntry("cash", "equity", 100),
    DoubleEntry("inventory", "cash", 90),
    DoubleEntry("cogs", "inventory", 60),
    MultipleEntry(
        debit=[SingleEntry("cash", Amount(75)), SingleEntry("refunds", Amount(2))],
        credit=[SingleEntry("sales", Amount(77))],
    ),
]

chart = Chart(
    income_summary_account="isa",
    retained_earnings_account="retained_earnings",
    assets=[Account("cash"), Account("inventory")],
    capital=[Account("equity")],
    expenses=[Account("cogs")],
    income=[Account("sales", contra_accounts=["refunds"])],
)

print(chart)
ledger = Ledger.new(chart)
ledger.post_many(entries)
print(ledger)
tb1 = ledger.trial_balance()
print(tb1)
assert tb1.tuples() == {
    "cash": (85, 0),
    "inventory": (30, 0),
    "equity": (0, 100),
    "retained_earnings": (0, 0),
    "sales": (0, 77),
    "refunds": (2, 0),
    "cogs": (60, 0),
    "isa": (0, 0),
}
_, ledger, income_summary = close(ledger, chart)
tb2 = ledger.trial_balance()
print("\n", tb2)
balances = tb2.balances()
print("\n", balances)
assert balances == {
    "cash": 85,
    "inventory": 30,
    "equity": 100,
    "retained_earnings": 15,
}
print(income_summary)

# NOTE: may need add more post close accounts (e.g. income tax posting)
