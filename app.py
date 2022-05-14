import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Accounting as Code",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("Accounting as Code")

"""Version 0.0.2 - concept review"""

st.header("1. Make a chart of accounts")

"""To specify an accounting system used provide names of the accounts used for:
   assets, expenses, capital, liabilities and income.

Example: `(Eq)uity` will create a shorthand `Eq` for Equity account.
"""
import re


def acronym(s):
    return re.findall("\((\w+)\)", s)[0].lower()


def ask(name, values):
    return [
        acronym(item) for item in st.text_input(name, value=values).split(" ") if item
    ]


assets = ask("Asset accounts", "(Cash) (Inv)entory")
# st.write(assets)

expenses = ask("Expenses accounts", "(COGS)")
# st.write(expenses)

capital = ask("Capital accounts", "(Eq)uity")
# st.write(capital)

liabilities = ask("Liabilities accounts", "")
# st.write(liabilities)

income = ask("Income accounts", "(Sales)")
# st.write(income)

from abacus.accounting import Chart, Entry

chart = Chart(assets, expenses, capital, liabilities, income)
book = chart.make_ledger()

f"""
Balance sheet equation:
"""
st.write(chart.equation)

st.header("2. Add entries")

"""An accounting entry is a record that changes one account on a debit side
and another on a credit side.
"""

entries_text = """300 Cash Eq "Add shareholder capital"
700 Cash D "Get loan"
800 Inv Cash "Acquire goods"
600 COGS Inv "Sold goods (expense)"
750 Cash Sales "Sold goods (income)" """

entries_text = st.text_area(
    "Specify a list of entries below in a format <amount> <debit account> <credit account>.",
    entries_text,
)


def get_parts(s):
    return re.findall(r"(.+)\s+\"(.+)\"", s)[0]


def split_entry_line(s):
    spec, desc = get_parts(s)
    value, debit, credit = spec.split()
    return Entry(int(value), debit.lower(), credit.lower(), desc)


from typing import List


def make_entries(entries_text) -> List[Entry]:
    entries = []
    for line in entries_text.split("\n"):
        if line:
            entry = split_entry_line(line)
            entries.append(entry)
    return entries


entries = make_entries(entries_text)
for entry in entries:
    book.process(entry)

st.header("3. Balance sheet")

from abacus.accounting import balance_lines
from abacus.formatting import side_by_side


selected_entry = st.select_slider(
    "Select step", entries, entries[-1], format_func=lambda e: e.description
)
index = [e.__dict__ for e in entries].index(selected_entry.__dict__)
entries_processed = entries[: index + 1]

showbook = chart.make_ledger()
for e in entries_processed:
    showbook.process(e)

left, right = balance_lines(showbook, chart)
st.code("\n".join(side_by_side(left, right)))

if st.checkbox("Show entries"):
    df = pd.DataFrame(entries_processed)
    df.index += 1
    st.dataframe(df)
