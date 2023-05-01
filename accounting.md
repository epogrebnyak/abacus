# Accounting equations explained 

## Balance sheet and income statement

Balance sheet and income statement are published financial reporting forms,
their equations are the following:

```
Assets = Capital + Liabilities   (1)
Profit = Income - Expenses       (2)
```

`(1)` shows the state of balance sheets at period end,
after closing entries are completed. It is also known as the [accounting identity][acc_i].

[acc_i]: https://en.wikipedia.org/wiki/Accounting_identity

`(1)` is always an instanteneous snapshot at a signle point in time 
and `(2)` always refers a flow of events that happened over a period of time.

## Trial balance

To keep track of events with the period before closing entries the following equation is helpful.

```
Assets = Capital + Profit + Liabilities                (3)
```

The profit in `(3)` is current period profit before closing entries. 

Why is profit recorded on the same side as capital? Here is one explaination. Profit is an increment of capital invested into the firm, 
so it appears next to equity. When no dividends are paid, all of the current profit will add to retained earnings, 
which is a component of capital.

Substituting `(2)` into `(3)` we get:

```
Assets = Capital + (Income - Expenses) + Liabilities   (4)
```

After rearranging we get the trial balance equation:

```
Assets + Expenses = Capital + Liabilities + Income     (5)
```

On the left we have the sum of so-called 'debit' accounts and on the left the sum of 
so-called 'credit' accounts. The trial balance equation should hold at any point in time.

## Decision to pay dividend or retain earnings

When an accounting period expires, the firm decides on what to do about profit. 
The firm has an option to pay the dividends to shareholdersor to keep the profit within the firm. 

If there are opportunities to earn more money by keeping money within the firm, 
it makes sense to pay no or little dividend and reinvest money 
into firm's profitable projects or lines of business.

If the shareholders do not see growth opportunities for the firm,
they are likely to decide to pay entire or larger amount of the profit 
as divivdends.

The decison to pay dividend is decided by shareholder vote based on 
management proposal. Differnt shareholders may have conflicting views about 
the proper amount of dividend. The amount of shareholder votes required
for dividend decision is regulated by firm articles of association and/or bylaws.

## Closing entries

The current period profit at period end will be distrubuted to dividends and retained earnings. 

This is done through closing entries. We will need more detailed accounts to keep track of 
these closing entries within our accounting equation system:

First, in capital we will distinguish shareholder equity, or paid-in capital,
and retained earnings.

```
Capital = Shareholder Equity + Retained Earnings       (6)
````

Second, we add income summary account. The income summary account is used to 'reset' income and expenses
at period end. The income summary account will show the amount of profit (or loss). 
The income and expenses accountts will be zero and ready to record business operations of the 
next period.

Third, we add dividends payable account will indicate the amount due to be paid to shareholders 
after the decision on amount of dividend is announced. 

With these changes the trail balance equation will look as following

```
Assets + Expenses = Shareholder Equity + Retained Earnings + Liabilities + Income + Income Summary Account + Dividend Payable
(7)
```

The closing entries will be the following:

1. We arrive at end of accounting period with Assets = a, Expenses = e, Shareholder Equity = s, Income = i and  Liabilities = l, and `a + e = s + i + l`. Assume this is the first year of operation and there are no retained earnings from earlier periods.
2. Move Income and Expenses to Income Summary Account. The accounts change to the following: Expenses = 0, Income = 0, Income Summary Account = i - e.   
3. Distribute profit from Income Summary Account into Retained Earnings and Dividend Payable accounts given the shareholder decision to pay d as dividend. Income Summary Account becomes 0, dividend payable becomes `d` and retained earning accrue by `r = (i - e) - d` (current profit less dividend). All of current profit is distributed and Income Summary Account becomes 0. Note that (i - e) = (r + d).
4. Pay the dividend due in cash. Assets decrease by d as cash was transfered to shareholders and dividend payable becomes 0 because the dividend due was actually paid out. This can also happen after closing entries.  

Steps 1-4 are demonstrated below using equation 7. The equation holds true at every step. 
```
    Assets + Expenses = Shareholder Equity + Retained Earnings + Liabilities + Income + Income Summary Account + Dividend Payable
1)  a        e          s                    0                   l             i        0                        0
2)  a        0          s                    0                   l             0        i - e                    0
3)  a        0          s                    r                   l             0        (i - e) - r - d = 0      d 
4)  a-d      0          s                    r                   l             0        0                        0      

Steps:
1) End of period, before closing entries
2) Open Income Summary Account, close Income and Expenses accounts
3) Distribute profit for Income Summary Account into Dividend Payable and Retained Earnings
4) Pay dividend in cash
```

At step 4 the trial balance equation (7) becomes the accounting identity (3), or the balance sheet as presented in a published report.


# A quick way to understand accounting for programmers

- [Small set of founding principles, or accounting axioms](#small-set-of-founding-principles-or-accounting-axioms)
- [Motivating example: a company lifecycle in 5 steps](#motivating-example-a-company-lifecycle-in-5-steps)
- [Accounting identity](#accounting-identity)
- [Reconciling with a traditional view](#reconciling-with-a-traditional-view)
- [Making accounting system realistic](#making-accounting-system-realistic)
- [Notes and comments](#notes-and-comments)

As a programmer, you might need a quick way to understand
how business transactions are recorded and presented in financial statements.
Given this knowledge one can create and support development
of accounting and financial reporting systems.

## Small set of founding principles, or accounting axioms

1. A firm keeps records of what the firm owns (assets) and sources of funds - equity (or capital) and liabilities (debt).

2. Equity and liabilities are records of amounts, or claims of shareholders and creditors on the firm. If a firm is instantly liquidated, these are the amounts of money the    shareholders and creditors should get.

3. Assets are records of what the firm owns and what can be converted to cash. There are current and fixed assets.

4. The firm aims to make profit and distribute all or part of this profit to shareholders as dividends. Shareholders may want to reinvest the profit if the firm business is growing.

5. We can devise a system that keeps a systematic record of assets, equity,
   liabilities and how the profit is formed.

6. The accounting principles must ensure the information about the firm is truthful.

## Motivating example: a company lifecycle in 5 steps

1. A commodity trading firm is created, shareholders pay in capital in cash.

```python
Assets = 1000 (Cash)
Equity = 1000 (Shareholder Equity)
Assets = Equity = 1000
```

2. The firm has bought a stock of commodities worth `900`.

```python
Assets = 100 (Cash) + 900 (Inventory)
Equity = 1000 (Shareholder Equity)
Assets = Equity = 1000
```

3. Commodities worth `700` were sold for `950`, making `250` in profit.

```python
Assets = 1050 (Cash) + 200 (Inventory)
Equity = 1000 (Shareholder Equity)
Profit = 250
Assets = Equity + Profit = 1250

Income(Sales) = 950
Expenses(Cost of goods sold, COGS) = 700
Profit = Income - Expenses = 250
```

4. The firm takes a `300` bank loan.

```python
Assets = 1350 (Cash) + 200 (Inventory)
Equity = 1000 (Shareholder Equity)
Profit = 250
Liabilities = 300 (Debt)
Assets = Equity + Profit + Liabilities = 1550
```

5. At financial year end the shareholders decide they will pay part of the
   profit as dividend and keep another part within the firm. The dividend is `150`, reinvested amount in `100`.

```python
Assets = 1200 (Cash) + 200 (Inventory)
Equity = 1000 (Shareholder Equity) + 100 (Retained Earnings)
Profit = 0
Liabilities = 300 (Debt)
Assets = Equity + Liabilities = 1400
```

## Accounting identity

Generalizing the steps above, accounts of the firm needs to keep track of the following equation:

```
Assets = Equity + Profit + Liabilities
```

Substituting and rearranging:

```
Profit = Income - Expenses
Assets = Equity + (Income - Expenses) + Liabilities
Assets + Expenses = Equity + Liabilities + Income
```

Below is a fundamental accounting identity:

```
Assets + Expenses = Equity + Liabilities + Income               (E1)
```

This equation should always hold true whenever a new accounting transaction is recorded.

Any accounting transaction can possibly only:

- increase an account on the left side, increase an account on the right side;
- increase some account on the left side, decrease another account on the left side;
- increase some account on the right side, decrease another account on the right side;
- decrease an account on the left side, decrease an account on the right side.

In any case the (E1) equation is just basic algebra. If the equation breaks, then a transaction was not recorded properly and should enter the accounting books differently. Another way of saying the same thing is that (E1) reflects the principle of double-entry bookkeeping: any accounting transaction (entry) always alters two accounts and preserves the accounting identity.

## Reconciling with a traditional view

An accounting identity [is usually shown][wiki] without profit account:

[wiki]: https://en.wikipedia.org/wiki/Accounting_identity

```
Assets = Equity + Liabilities
```

This identity shows the company balance sheet at the end of accounting period (at step 5), not within the period (steps 1-4). To make a working ledger of accounts we need equation (E1).

Here is a mindmap to reconcile the equations. We rename "equity" to "сapital" for better variable names.

```
Within the period        Period end
------------------       ------------------------------- --------------


Extended accounting
identity,                                      Accounting identity,
"brutto balance"                               balance sheet statement
(not published)                                (published)
A + E = C + L + I   ->   Profit is        ->    A = C + L
                         distributed
                         to dividend and
                         retained earnings

Income statement
(published)
P = I - E

A = Assets
E = Expenses
C = Capital (Equity)
L = Liabilities
I = Income
P = Profit
```

Traditional way of teaching accounting sometimes goes like this:

- a balance sheet is `A = C + L`;
- an income statement is `P = I - E`;
- they are related, but you spend few semesters in college until you figure out how;
- in a double entry accounting system every entry affects two accounts;
- accounting software guarantees nothing is lost.

Why not look the accounting identity as `A = C + L + (I - E)` and start applying algebraic rules even before knowing anything in accounting. This should really flatten 
the accounting learning curve!

## Making accounting system realistic

A "real" accounting system would need following additions to `E1`:

- distribution of current profit into dividend and retained earnings at period end;
- add accrual basis (receivables/payables);
- record valuation changes for fair value accounting;
- add depreciation/amortization and contraccounts (eg `Net PPE = PPE - Depreciation`);
- deferred taxes;
- deferred income or expenses;
- anything else?

## Notes and comments

- A firm keeps records of what the firm owns (assets) and sources of funds: shareholder equity (or capital) and liabilities (debt).

- Capital and liabilities indicate where money came from and where they should be distributed if the firm is liquidated. Capital and liаbilities are the records of claims on the firm.

- Shareholder equity is funds provided by firm owners. The shareholder expects the firm will make a profit and distribute all or part of this profit back to shareholders as dividend.

- Liabilities are financial obligations of the firm, these are the records of the debts that a firm owes to other parties. For example, when a firm takes a loan for a bank it is reflected as a liability.

- Asset is everything that is owned by the firm and what can be converted into cash. Assets are classified into fixed assets (like property, plant, equipment, or PPE) and current assets (like cash and inventory - raw material, work in progress and finished goods).

- Traditionally, an accounting identity is written as `Assets = Equity + Liabilities`.
  This is a published form of balance sheet statement at the end of an accounting period
  (eg a year). We do not see the current period profit as it was distributed to dividend and retained earnings and does not appear on a balance sheet.

- Profit of the firm is revenue (or sales, or income) less expenses: `Profit = Income - Expenses`. The report containing this data is known as income statement. The income statement shows the performance of the company over a period of time, typically a year, and it includes the current period profit. At period end the profit (net income) is either transferred to the balance sheet as retained earnings or paid out as dividend.

- Why is profit recorded on the same side as equity? Profit is an increment of capital invested into the firm, so it appears next to equity. When no dividends are paid, all of the current profit will add to retained earnings, which is a component of equity.

- There are 5 types of accounts:

  - assets
  - equity
  - liabilities
  - income
  - expenses

- These accounts are linked in the following way. Within a reporting period, the accounting equation can be written as `Assets = Equity + Profit + Liabilities`, where `Profit` is the current period profit.

- Substituting `Profit = Income - Expenses` into the equation above and rearranging we get the extended form of the accounting identity: `Assets + Expenses = Equity + Liabilities + Income`

- This equation should always hold true whenever a new accounting transaction is recorded, as it reflects the basic principles of double-entry bookkeeping. This is not a financial reporting form, unlike balance sheet and income statement.

- After we add detail into each type of account we will get a ledger of accounts ready to record transactions. A simple example:

```
Assets = Cash + Inventory
Expenses = Cost of Goods Sold (COGS)
Equity = Shareholder Equity
Income = Sales
(no fixed assets, no debt, no receivables/payables).
```

- Accounting equation:

```
Cash + Inventory + Cost of Goods Sold (COGS) = Shareholder Equity + Sales
```
