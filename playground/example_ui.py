from ui import AccountBalancesStore, Book

book = Book("Duffin Mills")
book.chart.add_asset("cash")
book.chart.add_asset("inventory")
book.chart.add_asset("ar", title="Accounts receivable")
book.chart.add_capital("equity", offsets=["ts"])
book.chart.set_title("ts", "Treasury shares")
book.chart.add_income("sales", offsets=["refunds", "cashback"])
book.chart.add_expense("cogs", title="Cost of goods sold")
book.chart.add_expense("salaries")
book.chart.add_expense("cit", title="Income tax")
book.chart.add_liability("vat", title="VAT payable")
book.chart.add_liability("dividend")
book.chart.add_liability("cit_due", title="Income tax payable")
book.chart.set_retained_earnings("re")
book.chart.set_income_summary_account("_isa")
book.open()
book.entry("Shareholder investment").amount(1500).debit("cash").credit(
    "equity"
).commit()
book.account_balances.to_file(filename="balances.json")
book.chart.to_file(filename="chart.json")

book = Book("Duffin Mills")
book.chart = book.chart.from_file(filename="chart.json")
opening_balances = AccountBalancesStore.from_file(filename="balances.json")
assert opening_balances.data["cash"] == 1500
assert opening_balances.data["equity"] == 1500
book.open(opening_balances={"cash": 1500, "equity": 1500})
# fmt: off
book.entry("Bought inventory (no VAT)").amount(1000).debit("inventory").credit("cash").commit()
book.entry("Invoice with 20% VAT").debit("ar", 1200).credit("sales", 1000).credit("vat", 200).commit()
book.entry("Registered costs").amount(600).debit("cogs").credit("inventory").commit()
book.entry("Accepted payment").amount(900).credit("ar").debit("cash").commit()
book.entry("Made refund").amount(50).debit("refunds").credit("ar").commit()
book.entry("Made cashback").amount(50).debit("cashback").credit("cash").commit()
book.entry("Paid salaries").amount(150).credit("cash").debit("salaries").commit()
assert book.proxy_net_earnings == 150
book.entry("Accrue corporate income tax 20%").amount(30).credit("cit_due").debit("cit").commit()
book.close()
book.entry("Bought back shares").amount(30).debit("ts").credit("cash").commit()
book.entry("Announced dividend").amount(60).debit("re").credit("dividend").commit()
book.entry("Pay corporate income tax").amount(30).debit("cit_due").credit("cash").commit()
# fmt: on
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


book.save()
book2 = Book.load("Duffin Mills")
assert book2.entries == book.entries
assert book2.chart == book.chart
