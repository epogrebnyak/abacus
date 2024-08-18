from core import (
    EntryBase,
    MultipleEntry,
    UnbalancedEntry,
    Amount,
    AccountName,
    AbacusError,
)
from dataclasses import dataclass, field


@dataclass
class NamedEntry(EntryBase):
    """Create entry using .debit() and .credit() methods.

    The syntax is similar to 'medici' package (<https://github.com/flash-oss/medici>),
    but we added .amount() method to set default amount for the entry.
    """

    title: str
    _amount: Amount | int | float | None = None
    _unbalanced_entry: UnbalancedEntry = field(default_factory=UnbalancedEntry)

    def amount(self, amount: Amount | int | float):
        """Set default amount for this entry."""
        self._amount = Amount(amount)
        return self

    def _get(self, amount: Amount | int | float | None = None) -> Amount:
        try:
            return Amount(amount or self._amount)
        except TypeError:
            raise AbacusError(f"Amount must be provided, got {amount}.")

    def debit(
        self, account_name: AccountName, amount: Amount | int | float | None = None
    ):
        """Add debit entry or debit account name."""
        amount = self._get(amount)
        self._unbalanced_entry.debit(account_name, amount)
        return self

    def credit(
        self, account_name: AccountName, amount: Amount | int | float | None = None
    ):
        """Add credit entry or credit account name."""
        amount = self._get(amount)
        self._unbalanced_entry.credit(account_name, amount)
        return self

    @property
    def multiple_entry(self) -> MultipleEntry:
        return MultipleEntry(data=self._unbalanced_entry.data)
