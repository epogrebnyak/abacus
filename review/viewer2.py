# This file is intended to replace viewers.py

from dataclasses import dataclass, field
from typing import Callable

from rich.console import Console
from rich.table import Table as RichTable
from rich.text import Text

from abacus.core import Amount
from abacus.core import BalanceSheet as BS
from abacus.core import IncomeStatement as IS

@dataclass
class TextColumn:
    """Column for creating tables.
    Methods to manipulate a column include align and concatenate."""

    strings: list[str]

    @property
    def width(self):
        return max(len(s) for s in self.strings)

    def align(self, method: str, fill_char: str):
        """Generic method to align all strings in the column."""
        width = self.width  # avoid calculating width too many times

        def f(s):
            return getattr(s, method)(width, fill_char)

        return self.__class__([f(s) for s in self.strings])

    def align_left(self, fill_char=" "):
        """Align all strings to the left."""
        return self.align("ljust", fill_char)

    def align_right(self, fill_char=" "):
        """Align all strings to the right."""
        return self.align("rjust", fill_char)

    def align_center(self):
        """Align all strings to center."""
        return self.align("center", " ")

    def empty(self, n: int = 1):
        """Create a new column filled with `n` spaces."""
        return self.refill(" " * n)

    def add_right(self, string: str):
        """Add `string` to the right of the column."""
        return self + self.refill(string)

    def add_space(self, n: int = 1):
        """Add `n` spaces to the right of the column."""
        return self + self.empty(n)

    def add_space_left(self, n: int = 1):
        """Add `n` spaces to the left of the column."""
        return self.empty(n) + self

    def refill(self, text):
        """Create a new column where all strings are replaced by `text`."""
        return self.__class__([text] * len(self.strings))

    def merge(self, column):
        """Merge two columns into one."""
        return self.__class__([a + b for a, b in zip(self.strings, column.strings)])

    def __add__(self, column):
        return self.merge(column)

    def insert_top(self, text):
        """Insert text at the top of the column."""
        return self.__class__([text] + self.strings)

    def insert_bottom(self, text):
        """Insert text at the bottom of the column."""
        return self.__class__(self.strings + [text])

    def header(self, text):
        """Add a header line to the column."""
        return self.insert_top(text.center(self.width))

    def __str__(self):
        """Return a string representation of the column, ready to print ot screen."""
        return "\n".join(self.strings)



def transpose(xs):
    return list(map(list, zip(*xs)))


@dataclass
class String:
    s: str

    def __str__(self):
        return self.r
    
    def rich(self):
        return Text(self.s)


@dataclass
class Number:
    n: Amount

    def __str__(self):
        return str(self.n)
    
    def rich(self):
        return red(self.n)


@dataclass
class Cell:
    content: String | Number


@dataclass
class Format:...

@dataclass
class BoldF(Format):...

@dataclass
class OffsetF(Format):...

BOLD = BoldF()
OFFSET = OffsetF()

@dataclass
class Cell2:
    content: String | Number 
    formats: list[Format] = field(default_factory=list)

    def __str__(self):
        r = str(self.content)
        if OFFSET in self.formats:
            r = "  " + r
        return r    

    def rich(self):
        r = self.content.rich()
        if OFFSET in self.formats:
            r = Text("  ") + r
        if BOLD in self.formats:
            r = bold(r)
        return r    


class Bold(Cell):
    """Row with section header like Assets"""


class Offset(Cell):
    """Row with offset like '  Cash'."""

@dataclass
class Empty:
    ...

EMPTY = Cell2(String("")) 

def maps(f, xs):
    return list(map(f, xs))

def to_text(cell):
    match cell:
        case Bold(String(s)):
            return s
        case Bold(Number(n)):
            return str(n)
        case Offset(String(s)):
            return "  " + s
        case Offset(Number(n)):
            return str(n)
        case Empty():
            return ""
        case a:
            raise TypeError(a)

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
        case Bold(String(s)):
            return bold(s)
        case Bold(Number(n)):
            return bold(red(n))
        case Offset(String(s)):
            return Text("  " + s)
        case Offset(Number(n)):
            return red(n)
        case Empty():
            return Text("")
        case a:
            raise TypeError(a)


@dataclass
class PairColumn:
    xs : list[Cell] 
    ys: list[Cell]

    def __len__(self):
        return len(self.xs)

    @classmethod
    def new(cls, statement):
        return cls.from_dict(cls.from_statement(statement))

    @classmethod
    def from_dict(cls, d: dict):
        xs = []
        ys = []
        for k, vs in d.items():
            n = sum(vs.values())
            xs.append(Bold(String(k)))
            ys.append(Bold(Number(n)))
            for name, value in vs.items():
                xs.append(Offset(String(name)))
                ys.append(Offset(Number(value)))
        return cls(xs, ys)
   
    def text_table(self):
        a = TextColumn(maps(to_text, self.xs)).align_left().add_space(2)
        b = TextColumn(maps(to_text, self.ys)).align_right()
        return a+b
    
    def append_empty(self, n):
        e = Empty()
        for _ in range(n):
            self.xs.append(e)
            self.ys.append(e)
    
    def add_footer(self, s: str, n: Amount):
        self.xs.append(Bold(String(s)))
        self.ys.append(Bold(Number(n)))

    def rename(self, rename_dict = None):
        rename_dict = rename_dict or {}
        def g(s):
            return rename_dict.get(s, s).replace("_", " ").strip().capitalize()
        def m(cell, f):
            match cell:
                case Offset(String(s)):
                    return Offset(String(f(s)))
                case Bold(String(s)):
                    return Bold(String(f(s)))
                case a:
                    return a
        self.xs = [m(x, g) for x in self.xs]     

def from_statement(statement: BS | IS):
        match statement:
            case BS(assets, capital, liabilities):
                return [
                    dict(assets=assets),
                    dict(capital=capital, liabilities=liabilities),
                ]
            case IS(income, expenses):
                return [dict(income=income, expenses=expenses)]

def equalize_length(p1: PairColumn, p2: PairColumn):
    n = max(len(p1), len(p2))
    p1.append_empty(n-len(p1))
    p2.append_empty(n-len(p2))


@dataclass
class Viewer:

    def print(self, width: int|None = None):
        """Rich printing to console."""
        t = self.rich_table(width)
        Console().print(t)

    def __str__(self):
        prefix = ""
        if self.title:
            prefix = self.title + "\n"
        return prefix + str(self.text_table())
    
    @property
    def width(self):
        return max(map(len,str(self).split("\n")))


@dataclass
class ViewerIS(Viewer):
    statement: IS
    title: str | None = None
    rename_dict: dict[str, str] = field(default_factory=dict)

    @property
    def pair_columns(self):
            d = from_statement(self.statement)[0]
            pi = PairColumn.from_dict(d)
            pi.add_footer("current profit", self.statement.current_profit())
            pi.rename(self.rename_dict)
            return [pi]

    def text_table(self):
            return self.pair_columns[0].text_table()

    def rich_table(self, width):
            table = RichTable(title=self.title, box=None, width=width, show_header=False)
            table.add_column()
            table.add_column(justify="right", style="green")
            p1 = self.pair_columns[0]
            for a, b in zip(p1.xs, p1.ys):
                table.add_row(to_rich_text(a), to_rich_text(b))
            return table

@dataclass
class ViewerBS(Viewer):
    statement: BS
    title: str | None = None
    rename_dict: dict[str, str] = field(default_factory=dict)

    @property
    def pair_columns(self):
        ds = from_statement(self.statement)
        p1 = PairColumn.from_dict(ds[0])
        p2 = PairColumn.from_dict(ds[1])
        equalize_length(p1, p2)
        p1.add_footer("total", sum(self.statement.assets.values()))
        p2.add_footer("total", sum(self.statement.capital.values()) + sum(self.statement.liabilities.values()))
        p1.rename(self.rename_dict)
        p2.rename(self.rename_dict)
        return p1, p2
 
    def text_table(self):
        p1, p2 = self.pair_columns
        return p1.text_table().add_space(2) + p2.text_table()
    
    def rich_table(self, width=None):
            table = RichTable(title=self.title, box=None, width=width, show_header=False)
            table.add_column()
            table.add_column(justify="right", style="green")
            table.add_column()
            table.add_column(justify="right", style="green")
            p1, p2 = self.pair_columns
            for a, b, c, d in zip(p1.xs, p1.ys, p2.xs, p2.ys):
                table.add_row(to_rich_text(a), to_rich_text(b), 
                              to_rich_text(c), to_rich_text(d))
            return table

b = BS(
    assets=dict(cash=200),
    capital=dict(equity=150, retained_earnings=-20),
    liabilities=dict(loan=65, dd=5),
)
i = IS(income=dict(sales=40), expenses=dict(rent=25, salaries=35))
vb = ViewerBS(
    b,
    rename_dict=dict(assets="активы", cash="касса", dd="dividend due", total="итого"),
    title="Баланс",
)
vi = ViewerIS(i, "Income statement")

print(vb)
print(vi)
vb.print(max(vb.width, vi.width)+2)
vb.print()
vi.print(max(vb.width, vi.width)+2)
vi.print()


@dataclass
class ViewerTB(Viewer):
    trial_balance: dict[str, tuple[Amount, Amount]]
    rename_dict: dict[str, str] = field(default_factory=dict)
    headers: tuple[str, str, str] = "Account", "Debit", "Credit"
    title: str | None = None

    @property
    def debits(self) -> list[str]:
        return [str(d) for (d, _) in self.trial_balance.values()]

    @property
    def credits(self) -> list[str]:
        return [str(c) for (_, c) in self.trial_balance.values()]

    def account_names(self):
        return self.trial_balance.keys()

    def account_names_column(self, header):
        return (
            TextColumn(self.account_names())
            .add_space(1)
            .align_left(".")
            .add_right("...")
            .header(header)
        )

    def numeric_column(self, values, header):
        return TextColumn(values).align_right().add_space_left(3).header(header)

    def text_table(self):
        return (
            self.account_names_column(self.headers[0])
            + self.numeric_column(self.debits, self.headers[1])
            + self.numeric_column(self.credits, self.headers[2])
        )

    def rich_table(self, width=None):
            table = RichTable(title=self.title, box=None, width=width, show_header=True)
            table.add_column(header=self.headers[0])
            table.add_column(header=self.headers[1], justify="right", style="green")
            table.add_column(header=self.headers[2], justify="right", style="green")
            for a, b, c in zip(self.account_names(), self.debits, self.credits):
                print(a, b, c)
                #table.add_row(to_rich_text(a), to_rich_text(b), 
                #              to_rich_text(c))
            return table

vtb = ViewerTB(dict(cash=(100,0), equity=(0,100)))
print(vtb)
vtb.print()