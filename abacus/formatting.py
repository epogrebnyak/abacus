# pylint: disable=import-error
from dataclasses import dataclass
from typing import Dict
from abacus.core import BalanceSheet, IncomeStatement, AccountBalancesDict


@dataclass
class LineBase:
    text: str
    value: str


class Header(LineBase):
    pass


class Line(LineBase):
    pass


def longest(xs):
    return max(len(x) for x in xs)


def side_by_side(left, right, space="  "):
    from itertools import zip_longest

    width = longest(left)
    gen = zip_longest(left, right, fillvalue="")
    gen = [(x.ljust(width, " "), y) for x, y in gen]
    return [f"{x}{space}{y}" for x, y in gen]


def lineset0(xs, parts):
    def tot(items):
        return AccountBalancesDict(items).total()

    for part in parts:
        items = getattr(xs, part)
        yield Header(part, tot(items))
        for name, value in items.items():
            yield Line(name, value)


def rename_with(alt_dict={}):
    def mut(s):
        return alt_dict.get(s, s).capitalize().replace("_", " ")

    def f(line):
        line.text = mut(line.text)
        return line

    return f


def offset(line):
    match line:
        case Header(a, b):
            return (a, b)
        case Line(a, b):
            return ("- " + a, b)


def lineset(report, parts, alt_dict={}):
    abc = lineset0(report, parts)
    abc = map(rename_with(alt_dict), abc)
    abc = map(offset, abc)
    return list(abc)


def plain(xs):
    from tabulate import tabulate

    return tabulate(xs, tablefmt="plain").split("\n")


def concat(left, right):
    return "\n".join(side_by_side(plain(left), plain(right)))


@dataclass
class TextViewer:
    rename_dict: Dict

    def balance_sheet(self, bs):
        right = lineset(bs, ["capital", "liabilities"], self.rename_dict)
        left = lineset(bs, ["assets"], self.rename_dict)
        return concat(left, right)

    def income_statement(self, inc):
        fin = ("Net profit", inc.current_profit())
        left = lineset(inc, ["income", "expenses"], self.rename_dict) + [fin]
        right = []
        return concat(left, right)
