from dataclasses import dataclass
from abacus.accounting_types import Amount, AccountName, Entry
from typing import Tuple, List
from collections import UserDict


@dataclass
class NamedEntry:
    opcode: str
    amount: Amount


"""Pair of debit and credit account names."""
Pair = Tuple[AccountName, AccountName]


class Shortcodes(UserDict[str, Pair]):
    """A dictionary that holds names of typical entry templates (pairs).
    Methods allow to convert `NamedEntry("pay_capital", 1000)` to
    `Entry("cash", "capital", 1000)` for a single entry or a list of entries.
    """

    def make_entry(self, named_entry: NamedEntry) -> Entry:
        dr, cr = self[named_entry.opcode]
        return Entry(dr, cr, named_entry.amount)

    def make_entries(self, named_entries: List[NamedEntry]):
        return [self.make_entry(ne) for ne in named_entries]
