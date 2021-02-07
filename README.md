# abacus
Learn accounting from Python: T-accounts, ledger and chart of accounts

Check https://github.com/epogrebnyak/abacus/blob/main/abacus/example.py as working example:

1. Specify a system of accounts, similar to: 

```python
chart=Chart(assets=['cash'], 
            capital=['equity', 'retained_earnings'], 
            liabilities=['debt'], 
            income=['income'],
            expenses=['expenses'])
```
2. Initilise ledger `L = make_ledger(chart)`
3. Run transactions like `L.enter(debit='cash', credit='debt', value=50)
4. Show the resulting balance sheet, simiar to:
```
Assets                      Capital
  Cash.................. 17   Equity.............. 30
  Loans................. 80   Retained earnings...  0
  Interest receivable...  1   Provisions..........  6
                              Profit.............. -1
                            Liabilities
                              Current accounts....  3
                              Deposits............ 60
                              Interest payable....  0
```
