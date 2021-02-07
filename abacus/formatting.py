from dataclasses import dataclass
from itertools import zip_longest
from typing import Optional


@dataclass
class Line:
    text: str
    value: Optional[int]


def longest(xs):
    return max(len(x) for x in xs)


def println(strings):
    print(*strings, sep="\n")


from dataclasses import dataclass


@dataclass
class Formatter:
    longest_words: int
    longest_digits: int
    prepend_words: int = 2
    after_words: int = 3
    prepend_digits: int = 1

    def format_line(self, line):
        text = renamer(line.text)
        value = line.value
        return (
            " " * self.prepend_words
            + text.ljust(self.longest_words + self.after_words, ".")
            + " " * self.prepend_digits
            + str(value).rjust(self.longest_digits)
        )

    def width(self):
        return (
            self.longest_words
            + self.longest_digits
            + self.prepend_words
            + self.after_words
            + self.prepend_digits
        )


def make_formatter(lines):
    return Formatter(
        longest_words=longest(x.text for x in lines),
        longest_digits=longest(str(x.value) for x in lines),
    )


def mk_liner(data):
    f = make_formatter(data)

    def line(x):
        text, value = x
        return f.format_line(text, value)

    return line


def fmt(lines, formatter=None):
    if not formatter:
        formatter = make_formatter(lines)
    return [formatter.format_line(x) for x in lines]


def renamer(x):
    return x.replace("_", " ").capitalize()


def side_by_side(left, right):
    width = longest(left)
    gen = zip_longest(left, right, fillvalue="")
    return ["{} {}".format(x.ljust(width, " "), y) for x, y in gen]


if __name__ == "__main__":
    # from accounting import Ledger, DebitAccount
    # L = Ledger(accounts={'cash': DebitAccount(debit_items=[100, 5], credit_items=[80]),
    #                     'loans': DebitAccount(debit_items=[80], credit_items=[])})
    # L.get_line('cash')

    data = Line("abc", 100), Line("def_def", 100000)
    assert fmt(data) == ["  Abc.......    100", "  Def def... 100000"]

    data2 = [Line("eee", 5), Line("fff", 10), Line("zzzzzzz", 1000)]
    assert side_by_side(fmt(data), fmt(data2)) == (
        [
            "  Abc.......    100   Eee.......    5",
            "  Def def... 100000   Fff.......   10",
            "                      Zzzzzzz... 1000",
        ]
    )
    println(side_by_side(left=fmt(data), right=fmt(data2)))
