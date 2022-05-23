# Dict -> Chart -> Ledger -> [Entry] -> Ledger -> Balance -> str

# %%
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union

Value = int  # can be Decimal


def zero() -> Value:
    return 0


@dataclass
class AccountBase:
    name: str
    debits: List[Value] = field(default_factory=list)
    credits: List[Value] = field(default_factory=list)

    def debit(self, amount: Value):
        self.debits.append(amount)

    def credit(self, amount: Value):
        self.credits.append(amount)

    def balance(self):
        raise NotImplementedError


@dataclass
class DebitAccount(AccountBase):
    def balance(self):
        return sum(self.debits) - sum(self.credits)


class CreditAccount(AccountBase):
    def balance(self):
        return sum(self.credits) - sum(self.debits)


# %%
class Asset(DebitAccount):
    pass


class Capital(CreditAccount):
    pass


class Liability(CreditAccount):
    pass


class Income(CreditAccount):
    pass


class Expense(DebitAccount):
    pass


Account = Union[Asset, Capital, Liability, Income, Expense]

# %%
from pydantic import BaseModel


class Chart(BaseModel):
    """Chart of accounts."""

    assets: Dict[str, str]
    expenses: Dict[str, str]
    capital: Dict[str, str]
    liabilities: Dict[str, str]
    income: Dict[str, str]


# %%


@dataclass
class Line:
    text: str
    amount: Value


def line(account: Account):
    return Line(account.name, account.balance())


Ledger = Dict[str, Account]


def make_ledger(chart: Chart) -> Ledger:
    ledger = dict()
    pairs = [
        ("assets", Asset),
        ("expenses", Expense),
        ("capital", Capital),
        ("liabilities", Liability),
        ("income", Income),
    ]
    for attr, cls in pairs:
        for key, acc_name in getattr(chart, attr).items():
            ledger[key] = cls(acc_name)
    return ledger


#%%


@dataclass
class Balance:
    assets: List[Line]
    capital: List[Line]
    liabilities: List[Line]
    current_profit: Line


@dataclass
class Entry:
    amount: Value
    debit: str
    credit: str
    description: str = ""


def process_one(account_dict: Ledger, entry: Entry):
    account_dict[entry.debit].debit(entry.amount)
    account_dict[entry.credit].credit(entry.amount)
    return account_dict


def process(account_dict: Ledger, entries: List[Entry]):
    for entry in entries:
        account_dict = process_one(account_dict, entry)
    return account_dict


#%%
def pick(account_dict: Ledger, cls):
    return {key: acc for key, acc in account_dict.items() if isinstance(acc, cls)}


def pick_list(account_dict: Ledger, cls):
    return [a for a in pick(account_dict, cls).values()]


def assets(account_dict):
    return pick_list(account_dict, Asset)


def capital(account_dict):
    return pick_list(account_dict, Capital)


def liabilities(account_dict):
    return pick_list(account_dict, Liability)


def sum_balances(accounts):
    return sum([a.balance() for a in accounts])


def profit(account_dict):
    incomes = pick_list(account_dict, Income)
    expenses = pick_list(account_dict, Expense)
    profit = sum_balances(incomes) - sum_balances(expenses)
    return Line("Current profit", profit)


def lines(accounts):
    return [line(a) for a in accounts]


# Accounts -> Balance:
#%%
def make_balance(account_dict: Ledger) -> Balance:
    return Balance(
        lines(assets(account_dict)),
        lines(capital(account_dict)),
        lines(liabilities(account_dict)),
        profit(account_dict),
    )


#%%


@dataclass
class Formatter:
    longest_words: int
    longest_digits: int
    prepend_words: int = 2
    after_words: int = 3
    prepend_digits: int = 1

    def format_line(self, line):
        text, amount = line.text, line.amount
        return (
            " " * self.prepend_words
            + text.ljust(self.longest_words + self.after_words, ".")
            + " " * self.prepend_digits
            + str(amount).rjust(self.longest_digits)
        )

    def width(self):
        return (
            self.longest_words
            + self.longest_digits
            + self.prepend_words
            + self.after_words
            + self.prepend_digits
        )


def longest(xs):
    return max(len(x) for x in xs)


def make_formatter(lines: List[Line]):
    return Formatter(
        longest_words=longest(x.text for x in lines),
        longest_digits=longest(str(x.amount) for x in lines),
    )


def to_strings(lines, formatter=None):
    if not formatter:
        formatter = make_formatter(lines)
    return [formatter.format_line(x) for x in lines]


def side_by_side(left, right):
    from itertools import zip_longest

    width = longest(left)
    gen = zip_longest(left, right, fillvalue="")
    return ["{} {}".format(x.ljust(width, " "), y) for x, y in gen]


#%%
def left(b: Balance) -> List[str]:
    return ["Assets"] + to_strings(b.assets)


def right(b: Balance) -> List[str]:
    cap = b.capital + [b.current_profit]
    liab = b.liabilities
    f = make_formatter(cap + liab)
    res = ["Capital"] + to_strings(cap, f)
    if liab:
        res += ["Liabilities"] + to_strings(liab, f)
    return res


def as_table(b: Balance):
    return "\n".join(side_by_side(left(b), right(b)))
