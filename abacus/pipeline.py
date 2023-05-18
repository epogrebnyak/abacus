from dataclasses import dataclass, field
from typing import List

from abacus.accounting_types import Entry, Posting
from abacus.ledger import Ledger, process_postings


@dataclass
class Pipeline:
    """Construct a list of postings to a ledger using add_entries() method
    and methods for closing temporarily accounts or contraccounts.
    """

    start_ledger: Ledger
    postings: List[Posting] = field(default_factory=list)

    def add_entry(self, dr, cr, amount):
        entry = Entry(dr, cr, amount)
        self.postings.append(entry)

    def add_entries(self, entries: List[Entry]):
        self.postings.extend(entries)

    def run(self):
        return process_postings(self.start_ledger, self.postings)
