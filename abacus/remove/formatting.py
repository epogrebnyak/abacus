from dataclasses import dataclass, field
from itertools import zip_longest
from typing import Dict, List, Tuple

from abacus.remove.accounting import Chart, Ledger, profit


@dataclass
class Line:
    text: str
    value: str


@dataclass
class Formatter:
    longest_words: int
    longest_digits: int
    n_spaces_before_words: int = 2
    n_dots_after_words: int = 3
    n_spaces_before_digits: int = (1,)
    dot_fill_char: str = "."

    def format_line(self, line: Line):
        text = line.text.replace("_", " ").capitalize()
        value = line.value
        return (
            " " * self.n_spaces_before_words
            + text.ljust(
                self.longest_words + self.n_dots_after_words, self.dot_fill_char
            )
            + " " * self.n_spaces_before_digits
            + value.rjust(self.longest_digits)
        )

    def width(self):
        return (
            self.longest_words
            + self.longest_digits
            + self.n_spaces_before_words
            + self.n_dots_after_words
            + self.n_spaces_before_digits
        )


def longest(xs):
    return max(len(x) for x in xs)


def make_formatter(lines: List[Line]):
    return Formatter(
        longest_words=longest(x.text for x in lines),
        longest_digits=longest(x.value for x in lines),
        n_spaces_before_words=2,
        n_dots_after_words=3,
        n_spaces_before_digits=1,
        dot_fill_char=".",
    )


def side_by_side(left, right, space="  "):
    width = longest(left)
    gen = zip_longest(left, right, fillvalue="")
    return ["{}{}{}".format(x.ljust(width, " "), space, y) for x, y in gen]


def get_line(ledger, account_name) -> Line:
    value = str(ledger.balance(account_name))
    return Line(account_name, value)


def get_line_and_rename(line, rename_with) -> Line:
    try:
        return Line(rename_with[line.text], line.value)
    except KeyError:
        return line


def make_line(account_name, rename_with, ledger) -> Line:
    line = get_line(ledger, account_name)
    return get_line_and_rename(line, rename_with)


def make_pane(**kwargs):
    res = []
    all_lines = [v for values in kwargs.values() for v in values]
    f = make_formatter(all_lines)
    for key, lines in kwargs.items():
        res.append(key.capitalize())
        for line in lines:
            res.append(f.format_line(line))
    return res


def balance_lines(
    ledger: Ledger, chart: Chart, rename_with: Dict[str, str] = {}
) -> Tuple[List[str], List[str]]:
    def as_line(account_name):
        return make_line(account_name, rename_with, ledger)

    def lines(account_names):
        return [as_line(account_name) for account_name in account_names]

    profit_line = Line("profit", str(profit(ledger, chart)))
    right = make_pane(
        capital=lines(chart.equity) + [profit_line],
        liabilities=lines(chart.liabilities),
    )
    left = make_pane(assets=lines(chart.assets))
    return left, right


@dataclass
class Book:
    chart: Chart
    ledger: Ledger
    rename_with: Dict[str, str] = field(default_factory=dict)

    def line(self, account_name):
        return make_line(account_name, self.rename_with, self.ledger)

    def lines(self, account_names):
        return [self.line(account_name) for account_name in account_names]

    @property
    def profit(self):
        return profit(self.ledger, self.chart)

    def right(self) -> List[str]:
        profit_line = Line("profit", str(self.profit))
        return make_pane(
            capital=self.lines(self.chart.equity) + [profit_line],
            liabilities=self.lines(self.chart.liabilities),
        )

    def left(self) -> List[str]:
        return make_pane(assets=self.lines(self.chart.assets))

    def __str__(self):
        return "\n".join(side_by_side(self.left(), self.right()))


def make_book(chart, rename_with={}):
    return Book(chart, make_ledger(chart), rename_with)
