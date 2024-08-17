from core import (
    EntryBase,
    MultipleEntry,
    DebitEntry,
    CreditEntry,
    Amount,
    AccountName,
    AbacusError,
)
from dataclasses import dataclass, field


@dataclass
class NamedEntry(EntryBase):
    """Create entry using .debit() and .credit() methods.

    The syntax is similar to 'medici' package (<https://github.com/flash-oss/medici>).
    """

    title: str
    _amount: Amount | int | float | None = None
    _multiple_entry: MultipleEntry = field(default_factory=MultipleEntry)

    def amount(self, amount: Amount | int | float):
        """Set default amount for this entry."""
        self._amount = amount
        return self

    def _append(self, cls, name, amount):
        a = Amount(amount or self._amount)
        if not a:
            raise AbacusError("Amount is not defined.")
        entry = cls(name, a)
        self._multiple_entry.data.append(entry)
        return self

    def debit(self, name: AccountName, amount: Amount | int | float | None = None):
        """Add debit entry or debit account name."""
        return self._append(DebitEntry, name, amount)

    def credit(self, name: AccountName, amount: Amount | int | float | None = None):
        """Add credit entry or credit account name."""
        return self._append(CreditEntry, name, amount)

    @property
    def multiple_entry(self) -> MultipleEntry:
        return self._multiple_entry
