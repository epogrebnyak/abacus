import streamlit as st

st.header("Accounting with `abacus` :star:")

reply = st.chat_input("Provide abacus command")

from abacus import Chart, Report

chart = Chart(assets=["cash"], capital=["common_stock"])
ledger = chart.ledger()
ledger.post(debit="cash", credit="common_stock", amount=20000, title="Owner's investment")
report = Report(chart, ledger)
try:
    ledger.post(debit="cash", credit="common_stock", amount=20000, title="Owner's investment")
except:
    pass    

text = report.balance_sheet + reply if reply else ""
st.text(report.balance_sheet)
st.text(reply)