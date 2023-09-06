"""Income statement and balance sheet reports, created from ledger."""
from dataclasses import dataclass

# pylint: disable=missing-docstring
from typing import Dict, List, Tuple

from engine.accounts import Asset, Capital, Expense, Income, Liability
from engine.base import AccountName, Amount, total
from pydantic import BaseModel  # pylint: disable=import-error # type: ignore


class Report:
    def lines(self, attributes: List[str]) -> List["Line"]:
        lines = []
        for attr in attributes:
            dict_ = getattr(self, attr)
            # The header line shows sum of the items
            lines.append(HeaderLine(attr, total(dict_)))
            for name, value in dict_.items():
                lines.append(AccountLine(name, str(value)))
        return lines


class BalanceSheet(BaseModel, Report):
    assets: Dict[AccountName, Amount]
    capital: Dict[AccountName, Amount]
    liabilities: Dict[AccountName, Amount]

    @classmethod
    def new(cls, ledger):
        return BalanceSheet(
            assets=ledger.subset(Asset).balances(),
            capital=ledger.subset(Capital).balances(),
            liabilities=ledger.subset(Liability).balances(),
        )

    def view(self, rename_dict) -> str:
        return view_balance_sheet(self, rename_dict)


class IncomeStatement(BaseModel, Report):
    income: Dict[AccountName, Amount]
    expenses: Dict[AccountName, Amount]

    @classmethod
    def new(cls, ledger) -> "IncomeStatement":
        return IncomeStatement(
            income=ledger.subset(Income).balances(),
            expenses=ledger.subset(Expense).balances(),
        )

    def current_profit(self):
        return total(self.income) - total(self.expenses)

    def view(self, rename_dict) -> str:
        return view_income_statement(self, rename_dict)


def clean(s, rename_dict):
    return rename_dict.get(s, s).replace("_", " ").strip().capitalize()


@dataclass
class Line:
    text: str
    value: str

    def rename(self, rename_dict: Dict[str, str]):
        self.text = clean(self.text, rename_dict)
        return self


class HeaderLine(Line):
    pass


class AccountLine(Line):
    pass


class EmptyLine(Line):
    pass


def view_balance_sheet(report: BalanceSheet, rename_dict: Dict[str, str]) -> str:
    left = report.lines(["assets"])
    right = report.lines(["capital", "liabilities"])
    # rename lines
    left = [line.rename(rename_dict) for line in left]
    right = [line.rename(rename_dict) for line in right]
    # make left and right same number of lines
    n = max(len(left), len(right))
    left += [EmptyLine("", "")] * (n - len(left))
    right += [EmptyLine("", "")] * (n - len(right))
    # Add end line
    h1 = HeaderLine("Total:", total(report.assets))
    left.append(h1)
    h2 = HeaderLine("Total:", total(report.capital) + total(report.liabilities))
    right.append(h2)
    a, b = to_columns(left)
    col1 = a.align_left(".").add_right("... ") + b.align_right()
    c, d = to_columns(right)
    col2 = c.align_left(".").add_right("... ") + d.align_right()
    return (col1.add_space(2) + col2).printable()


def view_income_statement(report: IncomeStatement, rename_dict: Dict[str, str]) -> str:
    left = report.lines(["income", "expenses"])
    # rename lines
    left = [line.rename(rename_dict) for line in left]
    # Add end line
    h1 = HeaderLine("Current profit:", report.current_profit())
    left.append(h1)
    a, b = to_columns(left)
    col = a.align_left(fill_char=".").add_right("... ") + b.align_right(fill_char=" ")
    return col.printable()


def offset(line: Line) -> Tuple[str, str]:
    match line:
        case HeaderLine(a, b):
            return (a, str(b))
        case AccountLine(a, b):
            return ("  " + a, str(b))
        case EmptyLine(_, _):
            return ("", "")


def to_columns(lines: List[Line]) -> Tuple[List[str], List[str]]:
    return Column([offset(line)[0] for line in lines]), Column(
        [offset(line)[1] for line in lines]
    )


@dataclass
class Column:
    strings: List[str]

    @property
    def width(self):
        return max(len(s) for s in self.strings)

    def align_left(self, fill_char=" "):
        return Column([s.ljust(self.width, fill_char) for s in self.strings])

    def align_right(self, fill_char=" "):
        return Column([s.rjust(self.width, fill_char) for s in self.strings])

    def empty(self, n: int = 1):
        return self.refill(" " * n)

    def add_right(self, string: str):
        return self + self.refill(string)

    def add_space(self, n: int = 1):
        return self + self.empty(n)

    def add_space_left(self, n: int = 1):
        return self.empty(n) + self

    def refill(self, text):
        return Column([text] * len(self.strings))

    def merge(self, column):
        return Column([a + b for a, b in zip(self.strings, column.strings)])

    def __add__(self, column):
        return self.merge(column)

    def header(self, text):
        return Column([text.center(self.width)] + self.strings)

    def printable(self):
        return "\n".join(self.strings)


def view_trial_balance(chart, ledger):
    data = list(ledger.yield_trial_balance())
    col_1 = (
        Column([chart.compose_name(d[0]) for d in data])
        .align_left(".")
        .add_space(1)
        .header("Account")
    )
    col_2 = (
        Column([str(d[1]) for d in data])
        .align_right()
        .add_space_left(2)
        .header("Debit")
        .add_space(2)
    )
    col_3 = (
        Column([str(d[2]) for d in data])
        .align_right()
        .add_space_left(2)
        .header("Credit")
    )
    return (col_1 + col_2 + col_3).printable()
