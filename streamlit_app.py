# How to run:
# git clone https://github.com/epogrebnyak/abacus.git
# pip install -e .
# streamlit run streamlit_app.py

import streamlit as st

from abacus import Chart, Report
from abacus.core import Entry

if "entries" not in st.session_state:
    st.session_state["entries"] = []


def as_integer(a: str):
    try:
        return int(a)
    except ValueError:
        return None


labels = ["cash", "ar", "inventory", "equity", "sales", "cogs", "sga"]
with st.sidebar:
    st.header("Post double entry :abacus:")
    with st.form("add_entry"):
        dr = st.selectbox("Debit:", labels, index=0)
        cr = st.selectbox("Credit:", labels, index=3)
        a = st.text_input("Amount (integer only)")
        submit = st.form_submit_button(label="Post entry")
        if submit:
            st.caption(f"Last posted: {dr}, {cr}, {a}")

if submit:
    if v := as_integer(a):
        st.session_state["entries"] += [Entry(dr, cr, v)]
    else:
        st.warning(f"Cannot process value: {a}")

st.header("Accounting with `abacus` :star:")

"""Use sidebar to post double entries and see how they affect financial reports."""


chart = Chart(
    assets=["cash", "ar", "inventory"],
    capital=["equity"],
    income=["sales"],
    expenses=["cogs", "sga"],
)
rename_dict = dict(
    ar="Accounts receivable",
    cogs="Cost of sales",
    sga="Selling, general and adm.expenses",
)


def live_reports():
    ledger = chart.ledger().post_many(st.session_state["entries"])
    report = Report(chart, ledger.condense())
    return (
        report.balance_sheet.viewer.use(rename_dict),
        report.income_statement.viewer.use(rename_dict),
        report.trial_balance,
    )


tab1, tab2, tab3 = st.tabs(["Balance sheet", "Income statement", "Trial balance"])

b, i, t = live_reports()

with tab1:
    st.text(b)

with tab2:
    st.text(i)

with tab3:
    st.text(t)

st.caption(
    """
This is an early demo of web interface for `abacus` package for accounting calculations.
[Visit Github](https://github.com/epogrebnyak/abacus), 
[read the docs](https://epogrebnyak.github.io/abacus/) 
and come back for more features.
Press `F5` or your browser `Reload` to restart this demo.  
© Evgeny Pogrebnyak, 2024."""
)
