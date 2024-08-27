from typing import Optional

from sqlmodel import Field, SQLModel, create_engine, Session, select

from enum import Enum
from decimal import Decimal
from pathlib import Path


class Side(str, Enum):
    debit = "debit"
    credit = "credit" 


class EntryHeader(SQLModel, table=True):
    count_id: Optional[int] = Field(default=None, primary_key=True)
    title: str

class SingleEntry(SQLModel, table=True):
    count_id: Optional[int] = Field(default=None, primary_key=True)
    side: Side
    account: str
    amount: Decimal
    header_id: int | None = Field(default=None, foreign_key="entryheader.count_id")


SE = SingleEntry
def dr(account: str, amount: Decimal, links_to:int) -> SingleEntry:
    return SE(side=Side.debit, account=account, amount=amount, header_id=links_to)

def cr(account: str, amount: Decimal, links_to:int) -> SingleEntry:
    return SE(side=Side.credit, account=account, amount=amount, header_id=links_to)

Path("db.sqlite").unlink(missing_ok=True)
engine = create_engine("sqlite:///db.sqlite", echo=False)
SQLModel.metadata.create_all(engine)
with Session(engine) as session:
    h = EntryHeader(title="Initial investment")
    session.add(h)
    session.commit()
    print("Created header:", x := h.count_id)
    e1 = dr("cash", 100, x)
    e2 = cr("equity", 100, x)
    print(e1, e2)
    session.add(e1)
    session.add(e2)
    session.commit()
    h = EntryHeader(title="More investment")
    e1.header_id = h.count_id
    e2.header_id = h.count_id
    session.add(dr("cash", 55, h.count_id))
    session.add(cr("cash", 55, h.count_id))
    session.commit()

def select_heroes():
    with Session(engine) as session:
        statement = select(SingleEntry)
        results = session.exec(statement)
        for hero in results:
            print(hero)

select_heroes()