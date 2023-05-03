from typing import List

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Accounting as Code",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("Accounting as Code")

"""Version 0.0.3 - concept review"""

st.header("1. Make a chart of accounts")

"""To specify an accounting system used provide names of the accounts used for:
   assets, expenses, capital, liabilities and income.

Example: `[Eq]uity` will create a shorthand `Eq` for Equity account. 
"""

from abacus.remove.formatting import side_by_side
from abacus.naming import variable


def as_dict(varline: str):
    return dict(variable(item) for item in varline.split(";"))


def ask(name, values):
    return as_dict(st.text_input(name, value=values))


assets_dict = ask("Asset accounts", "Cash; [Inv]entory")
expenses_dict = ask("Expenses accounts", "COGS; [Int]erest")
capital_dict = ask("Capital accounts", "[Eq]uity")
liabilities_dict = ask("Liabilities accounts", "Debt; Accrued interest [ai]")
income_dict = ask("Income accounts", "Sales")

from abacus.remove.accounting import Chart, Entry, make_book


def keys(d):
    return [k for k in d.keys()]


chart = Chart(
    assets=keys(assets_dict),
    expenses=keys(expenses_dict),
    capital=keys(capital_dict),
    liabilities=keys(liabilities_dict),
    income=keys(income_dict),
)
names_dict = {
    **assets_dict,
    **expenses_dict,
    **capital_dict,
    **liabilities_dict,
    **income_dict,
}
fullbook = make_book(chart, names_dict)
st.write(fullbook)

f"""
Balance sheet equation:
"""
st.write(chart.equation)

st.header("2. Add entries")

"""An accounting entry is a record that changes one account on a debit side
and another on credit side.
"""

entries_text = """300 Cash Eq "Add shareholder capital"
700 Cash Debt "Get loan"
800 Inv Cash "Acquire goods"
600 COGS Inv "Sold goods (expense)"
750 Cash Sales "Sold goods (income)" """

entries_text = st.text_area(
    'Specify a list of entries below in a format <amount> <debit account> <credit account> "<comment>".',
    entries_text,
)


def get_parts(s):
    import re

    return re.findall(r"(.+)\s+\"(.+)\"", s)[0]


def split_entry_line(s):
    spec, desc = get_parts(s)
    value, debit, credit = spec.split()
    return Entry(int(value), debit.lower(), credit.lower(), desc)


def make_entries(entries_text) -> List[Entry]:
    entries = []
    for line in entries_text.split("\n"):
        if line:
            entry = split_entry_line(line)
            entries.append(entry)
    return entries


entries = make_entries(entries_text)
fullbook.process_all(entries)

st.header("3. Balance sheet")

selected_entry = st.select_slider(
    "Select step", entries, entries[-1], format_func=lambda e: e.description
)
index = [e.__dict__ for e in entries].index(selected_entry.__dict__)
entries_processed = entries[: index + 1]

showbook = make_book(chart, names_dict)
showbook.process_all(entries)

s = "\n".join(side_by_side(*showbook.balance_lines()))
st.code(s)

if st.checkbox("Show entries"):
    df = pd.DataFrame(entries_processed)
    df.index += 1
    st.dataframe(df)

st.header("4. Try one transaction")
"""
...to see effect on balance sheet report.
"""

one_entry_text = st.text_input(
    'Enter transaction in a format <amount> <debit account> <credit account> "<comment>".',
    '0 Cash Eq "add more shareholder capital"',
)

showbook2 = make_book(chart, names_dict)
showbook2.process_all(entries + [split_entry_line(one_entry_text)])

left, right = showbook2.balance_lines()
st.code("\n".join(side_by_side(left, right)))
