"""Income statement and balance sheet reports, created from ledger."""
from dataclasses import dataclass
from typing import Dict, List, Tuple

from engine.accounts import Asset, Capital, Expense, Income, Liability
from engine.base import AccountName, Amount, total
from pydantic import BaseModel  # type: ignore
from rich.console import Console  # type: ignore
from rich.table import Table  # type: ignore
from rich.text import Text  # type: ignore


class Report:
    def lines(self, attributes: List[str]) -> List["Line"]:
        """Return list of lines for a given subset attributes.
        Allows to create a report with multiple columns,
        for example capital and liabilities on the left side of
        balance sheet."""
        lines: List[Line] = []
        for attr in attributes:
            dict_ = getattr(self, attr)
            # the header line shows sum of the items
            lines.append(HeaderLine(text=attr, value=str(total(dict_))))
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

    def print_rich(self, rename_dict: Dict[str, str]) -> None:
        left, right = left_and_right(self, rename_dict)
        table = make_table("Balance sheet", 80)
        for line_1, line_2 in zip(left, right):
            a, b = unpack(line_1)
            c, d = unpack(line_2)
            table.add_row(a, b, c, d)
        Console().print(table)


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

    def print_rich(self, rename_dict: Dict[str, str]) -> None:
        print_income_statement_rich(self, rename_dict)


def clean(s: str, rename_dict: Dict) -> str:
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


def left_and_right(
    report: BalanceSheet, rename_dict: Dict[str, str]
) -> Tuple[List[Line], List[Line]]:
    left = report.lines(["assets"])
    right = report.lines(["capital", "liabilities"])
    # rename lines
    left = [line.rename(rename_dict) for line in left]
    right = [line.rename(rename_dict) for line in right]
    # make left and right same number of lines
    n = max(len(left), len(right))
    left += [EmptyLine("", "")] * (n - len(left))
    right += [EmptyLine("", "")] * (n - len(right))
    # add end line
    h1 = HeaderLine("Total:", str(total(report.assets)))
    left.append(h1)
    h2 = HeaderLine("Total:", str(total(report.capital) + total(report.liabilities)))
    right.append(h2)
    return left, right


def view_balance_sheet(report: BalanceSheet, rename_dict: Dict[str, str]) -> str:
    left, right = left_and_right(report, rename_dict)
    a, b = to_columns(left)
    col1 = a.align_left(".").add_right("... ") + b.align_right()
    c, d = to_columns(right)
    col2 = c.align_left(".").add_right("... ") + d.align_right()
    return (col1.add_space(2) + col2).printable()


def red(b: str) -> Text:
    """Make digit red if negative."""
    v = Amount(b)
    if v and v < 0:
        return Text(b, style="red")
    else:
        return Text(b)


def bold(s: Text | str) -> Text:
    if isinstance(s, Text):
        s.stylize("bold")
        return s
    else:
        return Text(str(s), style="bold")


def unpack(line: Line) -> Tuple[Text, Text]:
    """Convert Line to rich.Text tuple"""
    match line:
        case HeaderLine(a, b):
            return bold(a), bold(red(b))
        case AccountLine(a, b):
            return ("  " + a, red(b))
        case EmptyLine(a, b):
            return ("", "")
        case _:
            raise ValueError(line)


def income_statement_lines(report: IncomeStatement, rename_dict: Dict[str, str]):
    left = report.lines(["income", "expenses"])
    # rename lines
    left = [line.rename(rename_dict) for line in left]
    # add end line
    h1 = HeaderLine("Current profit:", report.current_profit())
    left.append(h1)
    return left


def view_income_statement(report: IncomeStatement, rename_dict: Dict[str, str]) -> str:
    left = income_statement_lines(report, rename_dict)
    a, b = to_columns(left)
    col = a.align_left(fill_char=".").add_right("... ") + b.align_right(fill_char=" ")
    return col.printable()


def print_income_statement_rich(report: IncomeStatement, rename_dict: Dict[str, str]):
    left = income_statement_lines(report, rename_dict)
    table = Table(title="Income Statement", box=None, width=80, show_header=False)
    table.add_column("")
    table.add_column("", justify="right", style="green")
    for line in left:
        a, b = unpack(line)
        table.add_row(a, b)
    Console().print(table)


def offset(line: Line) -> str:
    match line:
        case HeaderLine(a, _):
            return a
        case AccountLine(a, _):
            return "  " + a
        case EmptyLine(_, _):
            return ""
    raise TypeError  # mypy wanted it


def to_columns(lines: List[Line]) -> Tuple["Column", "Column"]:
    return Column(list(map(offset, lines))), Column([line.value for line in lines])


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
    data = list(ledger._yield_tuples_for_trial_balance())
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


def make_table(title, width) -> Table:
    table = Table(title=title, box=None, width=width, show_header=False)
    table.add_column("")
    table.add_column("", justify="right", style="green")
    table.add_column("")
    table.add_column("", justify="right", style="green")
    return table
