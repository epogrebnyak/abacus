# abacus

[![pytest](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml/badge.svg)](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml)
[![PyPI](https://img.shields.io/pypi/v/abacus-py?color=blue)](https://pypi.org/project/abacus-py/)

A minimal yet valid double-entry accounting system in Python.

> [!TIP]
> Check out a brand new Streamlit demo for double-entry accounting at https://abacus.streamlit.app/ 

## Documentation

See project documentation at <https://epogrebnyak.github.io/abacus/>.

## Installation

```
pip install abacus-py
```

For latest version install from github:

```
pip install git+https://github.com/epogrebnyak/abacus.git
```

`abacus-py` requires Python 3.10 or higher.

## Quick example

Let's do Sample Transaction #1 from [accountingcoach.com](https://www.accountingcoach.com/accounting-basics/explanation/5)[^1].

[^1]: It is a great learning resource for accounting, highly recommended.

> On December 1, 2022 Joe starts his business Direct Delivery, Inc. The first transaction that Joe will record for his company is his personal investment of $20,000 in exchange for 5,000 shares of Direct Delivery's common stock.
> Direct Delivery's accounting system will show an increase in its account Cash from zero to $20,000, and an increase in its stockholders' equity account Common Stock by $20,000.

### Solution

Both Python code and command line script below will produce balance sheet after Sample Transaction #1 is completed.

Python code:

```python
from abacus import Chart, Report

chart = Chart(assets=["cash"], capital=["common_stock"])
ledger = chart.ledger()
ledger.post(debit="cash", credit="common_stock", amount=20000, title="Owner's investment")
report = Report(chart, ledger)
print(report.balance_sheet)
```

Command line script:

```bash
bx init
bx post --entry asset:cash capital:common_stock 20000 --title "Initial investment"
bx report --balance-sheet
```

### Result

```
Balance sheet
ASSETS  20000  CAPITAL              20000
  Cash  20000    Common stock       20000
                 Retained earnings      0
               LIABILITIES              0
TOTAL   20000  TOTAL                20000
```

See further transactions for this example at [documentation website](https://epogrebnyak.github.io/abacus/textbook/#accountingcoachcom).
