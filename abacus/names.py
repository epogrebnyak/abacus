"""Verbose account names."""

from pathlib import Path
from typing import Dict

from pydantic import BaseModel  # type: ignore

from abacus.accounting_types import AccountName


class Names(BaseModel):
    """Verbose account names."""

    names: Dict[AccountName, str] = {}

    def save(self, path):
        Path(path).write_text(self.json(indent=2), encoding="utf-8")
