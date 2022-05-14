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

st.header("Make a chart of accounts")

"""To specify an accounting system used provide names of the accounts used for:
- assets
- expenses
- capital
- liabilities
- income

Example: (Eq)uity will create a shorthand Eq for Equity account.
"""


def acronym(s):
    import re

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

st.header("Add entries")

"""An entry is a single accounting transaction that by defintion affects two accounts,
one on debit side, another on credit side.

Specify a list of entries below in a format <amount> <debit account> <credit account>: 
"""


entries_text = """300 Cash Eq
700 Cash D
800 Inv Cash
600 COGS Inv
750 Cash Sales"""

entries_text = st.text_area("Entries", entries_text)


def split_entry_line(s):
    value, debit, credit = s.split()
    return Entry(int(value), debit.lower(), credit.lower())


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

if st.checkbox("Show entries"):
    for entry in entries:
        st.write(entry)

from abacus.accounting import balance_lines
from abacus.formatting import side_by_side

left, right = balance_lines(book, chart)
st.markdown("```\n" + "\n".join(side_by_side(left, right)) + "\n```")


st.header("Small examples")

"""
Below are some simple examples to get used to [Streamlit][st].

All you do is adding `st.something(x)` to your code 
that will display `x` in the application.
"""


st.subheader("Input and display a number, show code")

with st.echo():
    x = st.number_input("A number please:")
    st.write("Just got", x)

st.subheader("Input and display a number, show code")

color = st.select_slider(
    "Select a color of the rainbow",
    options=["red", "orange", "yellow", "green", "blue", "indigo", "violet"],
)
st.write("My favorite color is", color)

st.subheader("Slider")

hour = st.slider("Hour", 0, 23, 12)

st.subheader("Display text, markdown, latex, variable, code")

st.write("<hr>")
st.text("Fixed width text")
st.markdown("_Markdown_")  # see *
st.latex(r"e^{i\pi} + 1 = 0")
st.write("Most objects")  # df, err, func, keras!
st.write(dict(a=1))
st.write(["st", "is <", 3])  # see *
st.title("My title")
st.header("My header")
st.subheader("My sub")
st.code("for i in range(8): foo()")

st.subheader("Line break")

st.markdown("---")

st.subheader("Graphviz chart")

# st.graphviz_chart(
#     """
#     digraph {
#         run -> intr
#         intr -> runbl
#         runbl -> run
#         run -> kernel
#         kernel -> zombie
#         kernel -> sleep
#         kernel -> runmem
#         sleep -> swap
#         swap -> runswap
#         runswap -> new
#         runswap -> runmem
#         new -> runmem
#         sleep -> runmem
#     }
# """
# )

st.subheader("Checkbox as collapse control")

if st.checkbox("Show raw data"):
    st.subheader("Raw data")

st.subheader("Input text")

with st.echo():
    name = st.text_input("Name")
    st.text(name)

st.subheader("Show dataframe or table")
st.write(
    pd.DataFrame({"first column": [1, 2, 3, 4], "second column": [10, 20, 30, 40]})
)

st.subheader("Now there is a chart")
chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
st.line_chart(chart_data)

st.subheader("Now there is a map")
map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4], columns=["lat", "lon"]
)
st.map(map_data)


def split_equation(s):
    return [[item.strip() for item in line.split("+")] for line in s.split("=")]


default_balance_eq = "(Cash) + (Inv)entory + (Exp)enses = (Eq)uity + (Sales)"
balance_str = st.text_input("What is your balance equation?", value=default_balance_eq)
aktiv, passiv = split_equation(s=balance_str)
st.write(aktiv)
st.write(passiv)
