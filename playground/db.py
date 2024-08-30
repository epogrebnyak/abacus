from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class Side(str, Enum):
    debit = "debit"
    credit = "credit"


class Header(SQLModel, table=True):
    count_id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    entries: list["Single"] = Relationship(back_populates="header")

    def debit(self, account: str, amount: Decimal):
        self.entries.append(Single(side=Side.debit, account=account, amount=amount))

    def credit(self, account: str, amount: Decimal):
        self.entries.append(Single(side=Side.credit, account=account, amount=amount))


class Single(SQLModel, table=True):
    count_id: Optional[int] = Field(default=None, primary_key=True)
    side: Side
    account: str
    amount: Decimal
    header_id: int | None = Field(default=None, foreign_key="header.count_id")
    header: Optional[Header] = Relationship(back_populates="entries")


def make_engine(filename: str = "db.sqlite", wipe: bool = False):
    if wipe:
        Path(filename).unlink(missing_ok=True)
    engine = create_engine(f"sqlite:///{filename}", echo=False)
    SQLModel.metadata.create_all(engine)
    return engine


def populate(session):
    h = Header(title="Initial investment")
    h.debit("cash", 100)
    h.credit("equity", 100)
    session.add(h)
    session.commit()
    print("Created header")
    print("  title:  ", h.title)
    print("  entries:", h.entries)


def query(session):
    statement = select(Single)
    results = session.exec(statement)
    for entry in results:
        print(entry)


engine = make_engine(wipe=True)
with Session(engine) as session:
    populate(session)
    query(session)


# Decimal('100.0000000000')
# Save accounts to Chart too
