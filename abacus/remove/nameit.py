from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union


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


# %%
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
