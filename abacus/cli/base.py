from abc import ABC
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import click


@dataclass
class Logger:
    """Logger will hold string messages about actions taken."""

    messages: List[str] = field(default_factory=list)

    def log(self, string: str):
        self.messages.append(string)

    def echo(self):
        for string in self.messages:
            print(string)


@dataclass
class BaseCommand(ABC):
    """Base class for chart and ledger commands."""

    path: Path
    logger: Logger = Logger(messages=[])

    def echo(self):
        self.logger.echo()
        return self

    def log(self, message):
        self.logger.log(message)
        return self

    def unlink(self):
        """Permanently delete file at *path*."""
        if self.path.exists():
            self.path.unlink()
            click.echo(f"Deleted {self.path}")
        else:
            click.echo(f"File not found: {self.path}")
