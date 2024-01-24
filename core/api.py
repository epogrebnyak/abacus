def short(accounts: list[str], re: str, t: list[str]):
    """Short names of arguments for nicer API query string."""
    return reports(accounts, re, t)


def reports(
    accounts: list[str], retained_earnings_account: str, transactions: list[str]
):
    """Return trial balance, balance sheet, and income statement."""
    return dict(
        accounts=accounts.split("+"),
        retained_earnings_account=retained_earnings_account,
        transactions=[t.split("+") for t in transactions],
    )


accounts = "asset:cash,ar+asset:ppe^depreciation+capital:equity+contra:equity:ts+liabilities:vat+income:sales"
re = "retained_earnings"
ts = ["cash,equity,500", "cr:vat,20+cr:sales,100+dr:cash,120"]
accepted = short(accounts, re, ts)
print(accepted)
assert accepted == {
    "accounts": [
        "asset:cash,ar",
        "asset:ppe",
        "capital:equity",
        "contra:equity:ts",
        "contra:ppe:depreciation",
        "liabilities:vat",
        "income:sales",
    ],
    "retained_earnings_account": "retained_earnings",
    "transactions": [["cash,equity,500"], ["cr:vat,20", "cr:sales,100", "dr:cash,120"]],
}
