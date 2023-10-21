from dataclasses import dataclass, field
from typing import List


@dataclass
class Logger:
    """Logger will hold string messages about actions taken."""

    messages: List[str] = field(default_factory=list)

    def log(self, string: str):
        self.messages.append(string)

    def echo(self):
        for string in self.messages:
            print(string)
