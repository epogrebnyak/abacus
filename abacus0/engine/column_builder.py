from dataclasses import dataclass
from typing import Callable, List


@dataclass
class Column:
    """Represent a column and add methods to manipulate it (including align and concatenate)."""

    strings: List[str]

    @property
    def width(self):
        return max(len(s) for s in self.strings)

    def apply(self, f: Callable):
        """Apply function `f` to each string in the column."""
        return Column([f(s) for s in self.strings])

    def align(self, method: str, fill_char: str):
        width = self.width  # avoid calultaing with many times

        def f(s):
            return getattr(s, method)(width, fill_char)

        return self.apply(f)

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
        return Column([text] * len(self.strings))

    def merge(self, column):
        """Merge two columns into one."""
        return Column([a + b for a, b in zip(self.strings, column.strings)])

    def __add__(self, column: "Column"):
        return self.merge(column)

    def insert_top(self, text):
        """Insert text at the top of the column."""
        return Column([text] + self.strings)

    def insert_bottom(self, text):
        """Insert text at the bottom of the column."""
        return Column(self.strings + [text])

    def header(self, text):
        """Add a header line to the column."""
        return self.insert_top(text.center(self.width))

    def printable(self):
        """Return a string representation of the column, ready to print ot screen."""
        return "\n".join(self.strings)

    def __str__(self):
        return self.printable()
