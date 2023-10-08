from dataclasses import dataclass
from typing import Callable, List


@dataclass
class Column:
    """Represent a column and add methods to manipulate it (including align and concatenate)."""

    strings: List[str]
    title: str = ""

    def set_title(self, title: str):
        """Set the title of the column."""
        self.title = title
        return self

    def drop_title(self):
        """Remove the title of the column."""
        self.title = ""
        return self

    @property
    def width(self):
        return max(len(s) for s in self.strings)

    def apply(self, f: Callable):
        """Apply function `f` to each string in the column."""
        return Column([f(s) for s in self.strings], self.title)

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
        return Column([text] * len(self.strings), self.title)

    def merge(self, column):
        """Merge two columns into one."""
        if not self.title and column.title:
            title = column.title
        elif self.title:
            title = self.title
        else:
            title = ""
        return Column([a + b for a, b in zip(self.strings, column.strings)], title)

    def __add__(self, column: "Column"):
        return self.merge(column)

    def insert_start(self, text):
        """Insert text at the start of the column."""
        return Column([text] + self.strings, self.title)

    def insert_end(self, text):
        """Insert text at the end of the column."""
        return Column(self.strings + [text], self.title)

    def header(self, text):
        """Add a header line to the column."""
        return self.insert_start(text.center(self.width))

    def markdown_header(self, text):
        width = max(len(text), self.width)
        return self.insert_start("-" * width).header(text)

    def markdown_separator(self):
        return self + self.refill(" | ")

    def printable(self):
        """Return a string representation of the column, ready to print ot screen."""
        if self.title:
            xs = [self.title + "\n"] + self.strings
        else:
            xs = self.strings
        return "\n".join(xs)

    def __str__(self):
        return self.printable()
