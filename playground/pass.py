from abacus import Book
from core import IncomeStatement
from pprint import pprint

cd = Book("Lost Data Ltd").add_asset("cash").add_income("sales", offsets=["refunds"]).open()
cd.double_entry("Regiter sales", "cash", "sales", 5).commit()
cd.double_entry("Issue refund", "refunds", "cash", 3).commit()
cd.close()
assert cd.income_statement == IncomeStatement(income={'sales': 2}, expenses={})
pprint(cd.save().load("Lost Data Ltd").income_statement)
