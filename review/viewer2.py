# This file is intended to replace viewers.py

from dataclasses import dataclass, field
from itertools import zip_longest

from rich.console import Console
from rich.table import Table as RichTable
from rich.text import Text

from abacus.core import Amount
from abacus.core import BalanceSheet as BS
from abacus.core import IncomeStatement as IS

# single column is a table and may be expanded
from abacus.viewers import Column as TextTable


def transpose(xs):
    return list(map(list, zip(*xs)))


@dataclass
class String:
    s: str


@dataclass
class Number:
    n: Amount


@dataclass
class Cell:
    content: String | Number


class BoldCell(Cell):
    """Row with section header like Assets"""


class OffsetCell(Cell):
    """Row with offset like '  Cash'."""


class EmptyCell:
    ...


Column = list[Cell]


@dataclass
class Table:
    """Внутреннее представление таблицы."""

    headers: list[str]
    columns: list[Column]
    title: str | None = None

    def merge_columns(self, t):
        e = EmptyCell()
        self.columns = transpose((zip_longest(*self.columns, *t.columns, fillvalue=e)))
        return self

    def apply_to_text(self, f):
        def g(cell):
            match cell:
                case OffsetCell(String(s)):
                    return OffsetCell(String(f(s)))
                case BoldCell(String(s)):
                    return BoldCell(String(f(s)))
                case a:
                    return a

        for i, column in enumerate(self.columns):
            self.columns[i] = [g(item) for item in column]
        return self

    def rename(self, rename_dict):
        def f(s):
            return rename_dict.get(s, s)

        return self.apply_to_text(f)

    def capitalize(self):
        def f(s):
            return s.replace("_", " ").strip().capitalize()

        return self.apply_to_text(f)


@dataclass
class Viewer:
    statement: BS | IS
    title: str | None = None
    rename_dict: dict[str, str] = field(default_factory=dict)

    @staticmethod
    def from_statement(statement: BS | IS):
        match statement:
            case BS(assets, capital, liabilities):
                return [
                    dict(assets=assets),
                    dict(capital=capital, liabilities=liabilities),
                ]
            case IS(income, expenses):
                return [dict(income=income, expenses=expenses)]

    @staticmethod
    def yield_items(d: dict):
        for k, vs in d.items():
            n = sum(vs.values())
            yield BoldCell(String(k)), BoldCell(Number(n))
            for name, value in vs.items():
                yield (OffsetCell(String(name)), OffsetCell(Number(value)))

    @property
    def table(self) -> Table:
        result = Table(headers=[], columns=[])
        for d in self.from_statement(self.statement):
            t = Table(headers=[], columns=transpose(self.yield_items(d)))
            result = result.merge_columns(t)
        return self.add_footer(result).rename(self.rename_dict).capitalize()

    def add_footer(self, table: Table) -> Table:
        match self.statement:
            case BS(a, c, l):
                t1 = sum(a.values())
                t2 = sum(c.values()) + sum(l.values())
                b = BoldCell(String("total"))
                v1 = BoldCell(Number(t1))
                v2 = BoldCell(Number(t2))
                table.columns[0].append(b)
                table.columns[1].append(v1)
                table.columns[2].append(b)
                table.columns[3].append(v2)
            case IS(i, e):
                b = BoldCell(String("profit"))
                table.columns[0].append(b)
                n = sum(i.values()) - sum(e.values())
                v = BoldCell(Number(n))
                table.columns[1].append(v)
        return table

    def text_table(self) -> TextTable:
        match self.statement:
            case BS(_, _, _):
                return from_columns_bs(self.table.columns)
            case IS(_, _):
                return from_columns_is(self.table.columns)

    def rich_table(self, width) -> RichTable:
        match self.statement:
            case BS(_, _, _):
                return rich_from_columns_bs(width, self.title, *self.table.columns)
            case IS(_, _):
                return rich_from_columns_is(width, self.title, *self.table.columns)

    def print(self, width: int):
        """Rich printing to console."""
        t = self.rich_table(width)
        Console().print(t)

    def __str__(self):
        prefix = ""
        if self.title:
            prefix = self.title + "\n"
        return prefix + str(self.text_table())


def from_columns_bs(columns: list[Column]):
    t1, t2, t3, t4 = [TextTable([to_text(cell) for cell in col]) for col in columns]
    t1 = t1.align_left(" ").add_space(2)
    t2 = t2.align_right(" ").add_space(2)
    t3 = t3.align_left(" ").add_space(2)
    t4 = t4.align_right(" ")
    return t1 + t2 + t3 + t4


def from_columns_is(columns: list[Column]):
    t1, t2 = [TextTable([to_text(cell) for cell in col]) for col in columns]
    t1 = t1.align_left(" ").add_space(2)
    t2 = t2.align_right(" ")
    return t1 + t2


def to_text(cell):
    match cell:
        case BoldCell(String(s)):
            return s
        case BoldCell(Number(n)):
            return str(n)
        case OffsetCell(String(s)):
            return "  " + s
        case OffsetCell(Number(n)):
            return str(n)
        case EmptyCell():
            return ""
        case a:
            raise TypeError(a)


def rich_from_columns_bs(width, title, c1, c2, c3, c4):
    table = RichTable(title=title, box=None, width=width, show_header=False)
    table.add_column("")
    table.add_column("", justify="right", style="green")
    table.add_column("")
    table.add_column("", justify="right", style="green")
    f = to_rich_text
    for a, b, c, d in zip(c1, c2, c3, c4):
        table.add_row(f(a), f(b), f(c), f(d))
    return table


def rich_from_columns_is(width, title, c1, c2):
    table = RichTable(title=title, box=None, width=width, show_header=False)
    table.add_column("")
    table.add_column("", justify="right", style="green")
    f = to_rich_text
    for a, b in zip(c1, c2):
        table.add_row(f(a), f(b))
    return table


def red(t: Amount) -> Text:
    """Make digit red if negative."""
    if t < 0:
        return Text(str(t), style="red")
    else:
        return Text(str(t))


def bold(s: Text | str) -> Text:
    if isinstance(s, Text):
        s.stylize("bold")
        return s
    else:
        return Text(str(s), style="bold")


def to_rich_text(cell) -> Text:
    match cell:
        case BoldCell(String(s)):
            return bold(s)
        case BoldCell(Number(n)):
            return bold(red(n))
        case OffsetCell(String(s)):
            return Text("  " + s)
        case OffsetCell(Number(n)):
            return red(n)
        case EmptyCell():
            return Text("")
        case a:
            raise TypeError(a)


# тестирование

b = BS(
    assets=dict(cash=200),
    capital=dict(equity=150, retained_earnings=-20),
    liabilities=dict(loan=65, dd=5),
)
i = IS(income=dict(sales=40), expenses=dict(rent=25, salaries=35))
v1 = Viewer(
    b,
    rename_dict=dict(assets="активы", cash="касса", dd="dividend due"),
    title="Баланс",
)
v2 = Viewer(i, "Income statement")

assert str(v1).split("\n") == [
    "Баланс",
    "Активы   200  Capital              130",
    "  Касса  200    Equity             150",
    "                Retained earnings  -20",
    "              Liabilities           70",
    "                Loan                65",
    "                Dividend due         5",
    "Total    200  Total                200",
]
assert str(v2).split("\n") == [
    "Income statement",
    "Income       40",
    "  Sales      40",
    "Expenses     60",
    "  Rent       25",
    "  Salaries   35",
    "Profit      -20",
]

# rich formatting
v1.print(width=80)
v2.print(width=80)
