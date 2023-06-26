# Workflow

`abacus` allows to specify a chart of accounts, create a ledger with starting balances,
post entries through accounting period, close accounts at period end and produce financial reports.

```mermaid
flowchart LR
  A["Chart"] --> B
  S["AccountBalances\n(start of period)"] --> B("Ledger")
  B --> C
  subgraph "Accounting Period"
    C["List[BusinessEntry]"]
  end
  C --> F
  subgraph "Period Closing"
     F["List[AdjustmentEntry]"]
     D["List[ClosingEntry]"]
  end
  F --> D
  D --> E(Ledger)
  E --> R1
  E --> R2
  E --> R3
  subgraph Reports
    R1(BalanceSheet)
    R2(IncomeStatement)
    R3("AccountBalances\n(end of period)")
  end
```
