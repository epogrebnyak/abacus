from pydantic import BaseModel
from abacus.accounting_types import Posting, Entry
from pathlib import Path
from typing import List

class Entries(BaseModel):
    postings: List[Posting] = []

    def add_entry(self, dr, cr, amount):
        entry = Entry(dr, cr, amount)
        self.postings.append(entry)
        return self

    def add_entries(self, entries):
        self.postings.extend(entries)    
        return self

    def save(self, path):
        Path(path).write_text(self.json())
    
