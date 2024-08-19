from ui import Book

book = Book("Duffin Mills")
book.add_asset(["cash", "ar", "inventory"])
book.add_capital("equity", offsets=["buyback"])
book.add_income("sales", offsets=["refunds", "cashback"])
book.add_expense(["cogs", "salaries", "cit"])
book.add_liability(["vat", "dividend", "cit_due"])
book.set_retained_earnings("re")
book.open()
# fmt: off
n = 1
for _ in range(n):
    book.entry("Shareholder investment").amount(1500).debit("cash").credit("equity").commit()
    book.entry("Bought inventory").amount(1000).debit("inventory").credit("cash").commit()
    book.entry("Invoice with VAT").debit("ar", 1200).credit("sales", 1000).credit("vat", 200).commit()
    book.entry("Registered costs").amount(600).debit("cogs").credit("inventory").commit()
    book.entry("Accepted payment").amount(900).credit("ar").debit("cash").commit()
    book.entry("Made refund").amount(50).debit("refunds").credit("ar").commit()
    book.entry("Made cashback").amount(45).debit("cashback").credit("cash").commit()
    book.entry("Paid salaries").amount(150).credit("cash").debit("salaries").commit()
    assert book.proxy_net_earnings == 155
    book.entry("Accrue corporate income tax").amount(30).credit("cit_due").debit("cit").commit()
book.close()
book.entry("Bought back shares").amount(100).debit("buyback").credit("cash").commit()
book.entry("Announced dividend").amount(15).debit("re").credit("dividend").commit()
# fmt: on
if n == 1:
    assert book._current_id == 11
    print((a := book.income_statement).json())
    assert a == {
        "income": {"sales": 905},
        "expenses": {"cogs": 600, "salaries": 150, "cit": 30},
    }
    print((b := book.balance_sheet).json())
    assert b == {
        "assets": {"cash": 1105, "ar": 250, "inventory": 400},
        "capital": {"equity": 1400, "re": 110},
        "liabilities": {"vat": 200, "dividend": 15, "cit_due": 30},
    }
