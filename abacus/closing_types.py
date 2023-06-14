"""CloseContra classes (moved to separate module here to prevent circular imports)."""


from pydantic.dataclasses import dataclass

from abacus.accounting_types import BaseEntry


@dataclass
class ClosingEntry(BaseEntry):
    action: str = "closing_entry"


@dataclass
class CloseIncome(ClosingEntry):
    action: str = "close_income"


@dataclass
class CloseExpense(ClosingEntry):
    action: str = "close_expense"


@dataclass
class CloseISA(ClosingEntry):
    action: str = "close_isa"


@dataclass
class CloseContra(ClosingEntry):
    pass


@dataclass
class CloseContraIncome(CloseContra):
    action: str = "close_contra_income"


@dataclass
class CloseContraExpense(CloseContra):
    action: str = "close_contra_expense"


@dataclass
class CloseContraAsset(CloseContra):
    action: str = "close_contra_asset"


@dataclass
class CloseContraLiability(CloseContra):
    action: str = "close_contra_liability"


@dataclass
class CloseContraCapital(CloseContra):
    action: str = "close_contra_capital"
