A minimal, yet valid double-entry accounting system in Python.

[![Reddit Discussion](https://img.shields.io/badge/Reddit-%23FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://www.reddit.com/r/Accounting/comments/136rrit/wrote_an_accounting_demo_in_python/)

## Quotes

> I think it's a great idea to mock-up a mini GL ERP to really get a foundational understanding of how the accounting in ERP works!

> I teach accounting information systems... I'd be tempted to use abacus as a way of simply showing the structure of a simple AIS.

> Hey, what a cool job, thanks much. Do you plan to make a possibility for RAS accounting?

## Accounting cycle

`abacus` enables to complete an accounting cycle in following steps.

1. Define a chart of accounts with five types of accounts (assets, expenses, capital, liabilities and income) and contra accounts (eg depreciation).
2. Create a blank general ledger for a new company or a general ledger with starting balances from previous period for existing company.
3. Post entries to a general ledger individually or in bulk.
4. View trial balance.
5. Make adjustment entries.
6. Close income and expenses accounts and transfer current period profit (loss) to retained earnings.
7. Make post-close entries (eg accrue dividend due to shareholders upon dividend announcement).
8. View and save income statement and balance sheet reports.
9. Save period end account balances and use them to initialize a general ledger at the start of a next accounting period.

More usage ideas in [Motivation](#motivation) section below.
