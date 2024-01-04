from abc import ABC
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import click


@dataclass
class BaseCommand(ABC):
    """Base class for chart and ledger commands."""

    path: Path
    messages: List[str] = field(default_factory=list)

    def echo(self):
        for string in self.messages:
            click.echo(string)
        return self

    def log(self, message):
        self.messages.append(message)
        return self

    def unlink(self):
        """Permanently delete file at *path*."""
        if self.path.exists():
            self.path.unlink()
            click.echo(f"Deleted {self.path}")
        else:
            click.echo(f"{self.path} not found.")

    def assert_does_not_exist(self):
        """Raise exception if file at *path* exists."""
        if self.path.exists():
            raise click.ClickException(f"{self.path} already exists.")
        else:
            return self
