import streamlit as st

st.header("Accounting with `abacus` :star:")

from abacus import Chart, Report
from abacus.core import Entry
from abacus.user_chart import UserChart

chart = Chart(assets=["cash"], capital=["common_stock"])
ledger = chart.ledger()
ledger.post(
    debit="cash", credit="common_stock", amount=20000, title="Owner's investment"
)
report = Report(chart, ledger)
st.text(report.balance_sheet)

import streamlit as st

with st.form("chart_form"):
    st.write("Define chart of accounts. Separate account names by space.")
    assets = st.text_input("Assets", value="cash ar goods")
    capital = st.text_input("Equity", value="common_stock")
    liabilities = st.text_input("Liabilities", value="ap")
    income = st.text_input("Income", value="sales")
    expenses = st.text_input("Expenses", value="cogs sga")
    st.form_submit_button("Create chart")

user_chart = UserChart.default().use(*assets.split(), prefix="asset")
user_chart.use(*capital.split(), prefix="capital")
user_chart.use(*liabilities.split(), prefix="liability")
user_chart.use(*income.split(), prefix="income")
user_chart.use(*expenses.split(), prefix="expense")
labels = [
    n
    for n in user_chart.names
    if n
    not in [
        chart.income_summary_account,
        chart.retained_earnings_account,
        chart.null_account,
    ]
]
st.write(labels)

if "entries" not in st.session_state:
    st.session_state["entries"] = []


def add_entry(dr, cr, a):
    st.session_state["entries"] += [Entry(dr, cr, a)]
    print_balance_sheet()


def print_balance_sheet():
    ledger2 = user_chart.chart().ledger().post_many(st.session_state["entries"])
    report2 = Report(user_chart.chart(), ledger2)
    st.text(report2.balance_sheet)


with st.form("ledger_form"):
    dr = st.selectbox("Account to debit", labels, index=0)
    cr = st.selectbox("Account to credit", labels, index=3)
    a = st.text_input("Amount")
    st.form_submit_button("Post entry", on_click=add_entry, args=(dr, cr, int(a or "0")))
    st.write(dr, cr, a)
    
# - may have just debit and credit and amount window below balance sheet and income statement
# - use chat for commands   
#st.write(st.session_state["entries"])
