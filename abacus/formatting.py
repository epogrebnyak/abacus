from dataclasses import dataclass
from itertools import zip_longest
from typing import Optional, List


@dataclass
class Line:
    text: str
    value: Optional[int]


def longest(xs):
    return max(len(x) for x in xs)


def println(strings):
    print(*strings, sep="\n")


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


def make_formatter(lines: List[Line]):
    return Formatter(
        longest_words=longest(x.text for x in lines),
        longest_digits=longest(str(x.value) for x in lines),
    )


def to_strings(lines, formatter=None):
    if not formatter:
        formatter = make_formatter(lines)
    return [formatter.format_line(x) for x in lines]


def renamer(x):
    return x.replace("_", " ").capitalize()


def side_by_side(left, right):
    width = longest(left)
    gen = zip_longest(left, right, fillvalue="")
    return ["{} {}".format(x.ljust(width, " "), y) for x, y in gen]
