from abacus.core import DebitAccount, CreditAccount, balance, Chart

def test_balance_on_DebitAccount():
    assert balance(DebitAccount([10, 10], [5])) == 15

def test_balance_on_CreditAccount():
    assert balance(CreditAccount([2, 2], [5, 4])) == 5

chart = Chart(
        assets=["cash", "receivables", "raw", "wip", "finished_goods", "fixed_assets"],
        expenses=["cogs", "sga", "interest"],
        equity=["equity", "retained_earnings"],
        liabilities=["debt", "accrued_interest", "payables"],
        income=["sales"],
        contraccounts=["depreciation"]
)

named_entries_dict=dict(
    add_capital=("cash", "equity"),
    buy_ppe=("fixed_assets", "cash"),
    invoice_raw=("raw", "payables"),
    pay_raw=("payables", "cash"),
    to_wip=("wip", "raw"),
    add_labor=("wip", "payables"),
    pay_labor=("payables","cash"),
    accrue_depr=("wip", "depreciation"),
    to_finished=("finished_goods", "wip"),
    invoice_sale=("receivables", "sales"),
    register_cogs=("cogs", "finished_goods"),
    accept_payment=("cash", "receivables")
)

named_entries = [
    ("add_capital", 2500),
    ("buy_ppe", 1200),
    ("invoice_raw", 800),
    ("pay_raw", 800),
    ("to_wip", 750),
    ("add_labor", 150),
    ("pay_labor", 150),
    ("accrue_depr", 100),
    ("to_finished", 1000),
    ("invoice_sale", 1800),
    ("register_cogs", 900), 
    ("accept_payment", 800),
    ("invoice_raw", 700),
    ("pay_raw", 700)
]


ledger = make_ledger(chart)
print(process_entry(ledger, Entry("cash", "equity", 1000)))
print(account_names(chart))
print(balances(ledger))
print(current_profit(ledger, chart))

