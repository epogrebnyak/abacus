"""CloseContra classes (moved to separate module here to prevent circular imports)."""

from typing import Dict, Type

from pydantic.dataclasses import dataclass

from abacus.accounting_types import BaseEntry
from abacus.accounts import Asset, Capital, Expense, Income, Liability, RegularAccount


@dataclass
class ClosingEntry:
    pass


@dataclass
class CloseIncome(BaseEntry, ClosingEntry):
    action: str = "close_income"


@dataclass
class CloseExpense(BaseEntry, ClosingEntry):
    action: str = "close_expense"


@dataclass
class CloseISA(BaseEntry, ClosingEntry):
    action: str = "close_isa"


@dataclass
class CloseContra(ClosingEntry):
    pass


@dataclass
class CloseContraIncome(BaseEntry, CloseContra):
    action: str = "close_contra_income"


@dataclass
class CloseContraExpense(BaseEntry, CloseContra):
    action: str = "close_contra_expense"


@dataclass
class CloseContraAsset(BaseEntry, CloseContra):
    action: str = "close_contra_asset"


@dataclass
class CloseContraLiability(BaseEntry, CloseContra):
    action: str = "close_contra_liability"


@dataclass
class CloseContraCapital(BaseEntry, CloseContra):
    action: str = "close_contra_capital"


def get_closing_entry_type(cls: Type[RegularAccount]) -> Type[CloseContra]:
    mapping: Dict[Type[RegularAccount], Type[CloseContra]] = dict(
        [
            (Income, CloseContraIncome),
            (Expense, CloseContraExpense),
            (Asset, CloseContraAsset),
            (Liability, CloseContraLiability),
            (Capital, CloseContraCapital),
        ]
    )
    return mapping[cls]
