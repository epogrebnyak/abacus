# Motivation, assumptions, implementation details



## Assumptions

Below are some simplifying assumptions and behaviors made for this code.
Some assumptions may be relaxed, some will remain a feature.

1. Account structure is flat, there are no subaccounts. To override one can use `cash:petty` and `cash:bank_account` to mimic subaccounts.

2. Every entry involves exactly two accounts, there are no compound entries.

3. No cash flow and changes in capital are reported.

4. There are no journals - all records go directly to general ledger.

5. Accounting entry is slim and has no information other than debit and credit accounts
   and entry amount. In future may add title, timestamp, hash and meta information.

6. Accounts balances can go to negative where they should not and there are no checks for entry validity.

7. We use [just one currency](https://www.mscs.dal.ca/~selinger/accounting/).

8. Account balances stay on one side, and do not migrate from one side to another.
   Credit accounts have credit balance, debit accounts have debit balance,
   and income summary account is a credit account.

9. Money amounts are integers, will change to `Decimal`.

10. Renamed accounts are dropped from the ledger. When `sales` becomes `net_sales`
    after a contra accounts like `discounts` are netted, `sales` leave the ledger,
    and `net_sales` remains.

## What things are realistic in this code?

1. Entries are stored in a queue and ledger state is calculated
   based on a previous state and a list of entries to be processed.

2. The chart of accounts can be fairly complex.

3. Chart of accounts may include contra accounts. Temporary contra accounts
   for income (eg discounts given) and expense (eg discounts or cashbacks received)
   are cleared at period end, permanent contra accounts
   (eg accumulated depreciation) are carried forward.

4. You can give a name to typical dr/cr account pairs and use this name to record transactions.

5. Accounts can be renamed for reporting purposes, thus opening a way to internationalisation.
   You can keep a short name like `cash` or account code in ledger and rename `cash` to `नकद` for a report.

## Implementation details

1. The code is covered by tests, linted and type annotated.

2. Data structures used are serialisable, so inputs and outputs can be stored and retrieved.

3. XML likely to be a format for accounting reports interchange, while JSON and YAML are intended for `abacus`.

4. Modern Python features such as subclasssing and pattern matching help to make code cleaner.
   Classes like `Asset`, `Expense`, `Capital`, `Liability`, `Income` pass forward useful information about account types and their behaviors.

5. This is experimental software. The upside is that we can make big changes fast. On a downside we do not learn (or earn) from users, at least yet.

6. `abacus` is not optimised for performance and likely to be slow under high load.
