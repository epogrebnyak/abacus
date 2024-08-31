from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


from core import T5, Side

class BaseAccount(SQLModel):
   name: str = Field(primary_key=True)
   title: str | None = None

class IncomeSummaryAccount(BaseAccount, table=True):
    ...

class RetainedEarningsAccount(BaseAccount, table=True):
    ...


class RegularAccount(BaseAccount, table=True):
    t5: T5

class ContraAccount(BaseAccount, table=True):
    offsets: str = Field(foreign_key="regularaccount.name") 
 
class Header(SQLModel, table=True):
    count_id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    entries: list["Single"] = Relationship(back_populates="header")

    def debit(self, account: str, amount: Decimal):
        self.entries.append(Single(side=Side.Debit, account=account, amount=amount))

    def credit(self, account: str, amount: Decimal):
        self.entries.append(Single(side=Side.Credit, account=account, amount=amount))


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
    isa = IncomeSummaryAccount(name="__isa__")
    re = RetainedEarningsAccount(name="re")
    session.add(isa)
    session.add(re)
    a1 = RegularAccount(name="cash", t5=T5.Asset)
    a2 = RegularAccount(name="equity", t5=T5.Capital)
    a3 = ContraAccount(name="ts", title="Treasury shares", offsets="equity")
    session.add(a1)
    session.add(a2)
    session.commit()
    session.add(a3)
    session.commit()
    print("Created header")
    print("  title:  ", h.title)
    print("  entries:", h.entries)


def query(session):
    statement = select(Single)
    results = session.exec(statement)
    for entry in results:
        print(entry)

from ui import Chart

def load_chart(session):
    isa = session.exec(select(IncomeSummaryAccount)).one()
    re = session.exec(select(RetainedEarningsAccount)).one()
    chart = Chart(income_summary_account=isa.name, retained_earnings_account=re.name)
    for account in session.exec(select(RegularAccount)):
        chart.add(t=account.t5, account_name=account.name, title=account.title)
    for contra_account in session.exec(select(ContraAccount)):
        chart.offset(contra_account.offsets, contra_account.name, contra_account.title)
    return chart    

def save_chart(session, chart):
    isa = IncomeSummaryAccount(name=chart.income_summary_account)
    re = RetainedEarningsAccount(name=chart.retained_earnings_account)
    session.add(isa)
    session.add(re)
    for account, (t, offsets) in chart.accounts.items():
        a = RegularAccount(name=account, t5=t, title=chart.names.get(account))
        session.add(a)
        for offset in offsets:
            c = ContraAccount(name=offset, offsets=account, title=chart.names.get(offset))
            session.add(c)
    session.commit()

engine = make_engine(wipe=True)
with Session(engine) as session:
    populate(session)
    query(session)
    chart = load_chart(session)
    print(chart)


# Decimal('100.0000000000')
# Save accounts to Chart too
