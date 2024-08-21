from ui import Book

book = Book("Duffin Mills")
book.add_asset("cash")
book.add_asset("inventory")
book.add_asset("ar", title="Accounts receivable")
book.add_capital("equity", offsets=["ts"])
book.set_title("ts", "Treasury shares")
book.add_income("sales", offsets=["refunds", "cashback"])
book.add_expense("cogs", title="Cost of goods sold")
book.add_expense("salaries")
book.add_expense("cit", title="Income tax")
book.add_liability("vat", title="VAT payable")
book.add_liability("dividend")
book.add_liability("cit_due", title="Income tax payable")
book.set_retained_earnings("re")
book.set_income_summary_account("_isa")
book.open()
# fmt: off
book.entry("Shareholder investment").amount(1500).debit("cash").credit("equity").commit()
book.entry("Bought inventory (no VAT)").amount(1000).debit("inventory").credit("cash").commit()
book.entry("Invoice with 20% VAT").debit("ar", 1200).credit("sales", 1000).credit("vat", 200).commit()
book.entry("Registered costs").amount(600).debit("cogs").credit("inventory").commit()
book.entry("Accepted payment").amount(900).credit("ar").debit("cash").commit()
book.entry("Made refund").amount(50).debit("refunds").credit("ar").commit()
book.entry("Made cashback").amount(50).debit("cashback").credit("cash").commit()
book.entry("Paid salaries").amount(150).credit("cash").debit("salaries").commit()
#from pprint import pprint
#pprint(book)
assert book.proxy_net_earnings == 150
book.entry("Accrue corporate income tax 20%").amount(30).credit("cit_due").debit("cit").commit()
book.close()
book.entry("Bought back shares").amount(30).debit("ts").credit("cash").commit()
book.entry("Announced dividend").amount(60).debit("re").credit("dividend").commit()
book.entry("Pay corporate income tax").amount(30).debit("cit_due").credit("cash").commit()
# fmt: on
assert book._current_id == 12
print((a := book.income_statement).json())
assert a.dict() == {
    "income": {"sales": 900},
    "expenses": {"cogs": 600, "salaries": 150, "cit": 30},
}
print((b := book.balance_sheet).json())
assert b.dict() == {
    "assets": {"cash": 1140, "ar": 250, "inventory": 400},
    "capital": {"equity": 1470, "re": 60},
    "liabilities": {"vat": 200, "dividend": 60, "cit_due": 0},
}
# book.save_chart()
# book.save_ledger()
