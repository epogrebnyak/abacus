<!-- markdownlint-disable -->

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `core`
Core elements of a minimal double-entry accounting system. 

Using this module you can: 


- create a chart of accounts using `Chart` class, 
- create `Ledger` from `Chart`, 
- post entries to `Ledger`, 
- generate trial balance, balance sheet and income statement. 

Implemented in this module: 


- **contra accounts** — there can be a `refunds` account that offsets `income:sales`  and `depreciation` account that offsets `asset:ppe`, 
- **multiple entries** — debit and credit several accounts in one transaction, 
- **closing entries** — proper closing of accounts at the accounting period end. 

Assumptions and simplifications: 

1. no sub-accounts — there is only one level of account hierarchy in chart 2. account names must be globally unique 3. no cashflow statement 4. one currency 5. no checks for account non-negativity 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L388"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `starting_entries`

```python
starting_entries(chart: Chart, balances: AccountBalances)
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L449"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `contra_pairs`

```python
contra_pairs(
    chart: Chart,
    contra_t: Type[ContraAccount]
) → list[tuple[str, str]]
```

Return list of account and contra account name pairs for a given type of contra account. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L659"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `sum_second`

```python
sum_second(xs)
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `T`
Five types of accounts and standard prefixes for account names. 





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Holder`
The `Holder` class is a wrapper to hold an account type  that would be convertible to T-account. 

Child classes are: 


- `Regular(Holder)` for regular accounts, 
- `Contra(Holder)` for contra accounts, 
- `Wrap(Holder)` for income summary and null account. 

This wrapping enables to pattern match on account type and make type conversions cleaner. 


---

#### <kbd>property</kbd> t_account

Provide T-account constructor. 




---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L71"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Regular`
Regular(t: core.T) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(t: T) → None
```






---

#### <kbd>property</kbd> t_account








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L92"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Contra`
Contra(t: core.T) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(t: T) → None
```






---

#### <kbd>property</kbd> t_account








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L113"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Account`
Account(name: str, contra_accounts: list[str] = <factory>) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(name: str, contra_accounts: list[str] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L118"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `from_string`

```python
from_string(s) → Account
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L128"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TAccount`
T-account will hold amounts on debits and credit side. 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L143"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance() → int
```

Return account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L147"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```

Create an entry that transfers account balance from this account to destination account. 

This account name is `my_name` and destination account name is `dest_name`. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L173"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `DebitAccount`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L177"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L181"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `CreditAccount`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L182"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L189"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RegularAccount`








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L193"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Asset`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L177"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L197"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Capital`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L182"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L201"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Liability`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L182"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L205"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Income`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L182"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L209"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Expense`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L177"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L213"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ContraAccount`








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L217"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ContraAsset`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L182"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L221"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ContraCapital`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L177"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L225"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ContraLiability`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L177"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L229"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ContraIncome`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L177"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L233"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ContraExpense`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L182"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L237"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ExtraAccount`








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L241"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ExtraCreditAccount`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L182"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L245"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `IncomeSummaryAccount`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L182"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L249"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `NullAccount`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L182"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L253"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ExtraDebitAccount`




<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[int] = <factory>, credits: list[int] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `balance`

```python
balance()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Create a new account of the same type with only one value as account balance. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `credit`

```python
credit(amount: int)
```

Add credit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `debit`

```python
debit(amount: int)
```

Add debit amount to account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty()
```

Create a new empty account of the same type. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `topup`

```python
topup(balance)
```

Add starting balance to a proper side of account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L177"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `transfer_balance`

```python
transfer_balance(my_name: str, dest_name: str) → Entry
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L257"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Wrap`
Holder for accounts that do not belong to any of 5 account types. 

There are two temporary accounts where this holder is needed: 


   - income summary account, 
   - null account. 

Note: Income summary account should have zero balance at the end of accounting period. Null account should always has zero balance. 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(t: type[ExtraAccount]) → None
```






---

#### <kbd>property</kbd> t_account








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L277"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Chart`
Chart of accounts. 



**Example:**
 

```python
chart = Chart(assets=["cash"], capital=["equity"])
``` 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    income_summary_account: str = '_isa',
    retained_earnings_account: str = 'retained_earnings',
    null_account: str = '_null',
    assets: list[str | Account] = <factory>,
    capital: list[str | Account] = <factory>,
    liabilities: list[str | Account] = <factory>,
    income: list[str | Account] = <factory>,
    expenses: list[str | Account] = <factory>
) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L320"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `dict_items`

```python
dict_items()
```

Assign account types to account names. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L340"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ledger`

```python
ledger(starting_balances: dict | None = None)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L331"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `pure_accounts`

```python
pure_accounts(xs: list[str | Account]) → list[Account]
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L334"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `stream`

```python
stream(items, t: T)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L314"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `to_dict`

```python
to_dict() → dict[str, Holder]
```

Return a dictionary of account names and account types. Will purge duplicate names if found in chart. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L300"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `validate`

```python
validate() → Chart
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L344"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Entry`
Double entry with account name to be debited,  account name to be credited and transaction amount. 



**Example:**
 

```python
entry = Entry(debit="cash", credit="equity", amount=20000)
``` 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debit: str, credit: str, amount: int) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L363"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `from_string`

```python
from_string(line: str)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L360"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `to_json`

```python
to_json()
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L368"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AccountBalances`







---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L377"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `json`

```python
json()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L383"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `load`

```python
load(path: Path | str)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L369"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `nonzero`

```python
nonzero()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L380"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `save`

```python
save(path: Path | str)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L374"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `total`

```python
total()
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L392"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Ledger`





---

#### <kbd>property</kbd> balances

Return account balances. 



---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L441"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `condense`

```python
condense()
```

Return a new ledger with condensed accounts that hold just one value. Used to avoid copying of ledger data where only account balances are needed. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L393"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `new`

```python
new(chart: Chart, balances: AccountBalances | None)
```

Create a new ledger from chart, possibly using starting balances. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L402"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `post`

```python
post(debit: str, credit: str, amount: int, title: str = '')
```

Post to ledger using debit and credit account names and amount. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L411"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `post_many`

```python
post_many(entries: Iterable[Entry])
```

Post several double entries to ledger. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L407"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `post_one`

```python
post_one(entry: Entry)
```

Post one double entry to ledger. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L431"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `subset`

```python
subset(cls: Type[TAccount])
```

Filter ledger by account type. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L466"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Pipeline`
A pipeline to accumulate ledger transformations. 

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L469"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(chart: Chart, ledger: Ledger)
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L474"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `append_and_post`

```python
append_and_post(entry: Entry)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L527"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `close`

```python
close()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L478"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `close_contra`

```python
close_contra(t: Type[ContraAccount])
```

Close contra accounts of type `t`. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L507"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `close_first`

```python
close_first()
```

Close contra income and contra expense accounts. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L497"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `close_isa_to_re`

```python
close_isa_to_re()
```

Close income summary account to retained earnings account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L520"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `close_last`

```python
close_last()
```

Close permanent contra accounts. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L513"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `close_second`

```python
close_second()
```

Close income and expense accounts to income summary account, then close income summary account to retained earnings. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L487"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `close_to_isa`

```python
close_to_isa()
```

Close income or expense accounts to income summary account. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L534"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Report`
Report(chart: core.Chart, ledger: core.Ledger, rename_dict: dict[str, str] = <factory>) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    chart: Chart,
    ledger: Ledger,
    rename_dict: dict[str, str] = <factory>
) → None
```






---

#### <kbd>property</kbd> account_balances





---

#### <kbd>property</kbd> balance_sheet





---

#### <kbd>property</kbd> balance_sheet_before_closing





---

#### <kbd>property</kbd> income_statement





---

#### <kbd>property</kbd> pipeline





---

#### <kbd>property</kbd> trial_balance







---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L572"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_all`

```python
print_all()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L542"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `rename`

```python
rename(key, value)
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L581"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Statement`





---

#### <kbd>property</kbd> viewer







---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L590"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print`

```python
print(width=None)
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L594"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `BalanceSheet`
BalanceSheet(assets: core.AccountBalances, capital: core.AccountBalances, liabilities: core.AccountBalances) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    assets: AccountBalances,
    capital: AccountBalances,
    liabilities: AccountBalances
) → None
```






---

#### <kbd>property</kbd> viewer







---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L606"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `new`

```python
new(ledger: Ledger)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L590"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print`

```python
print(width=None)
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L615"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `IncomeStatement`
IncomeStatement(income: core.AccountBalances, expenses: core.AccountBalances) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(income: AccountBalances, expenses: AccountBalances) → None
```






---

#### <kbd>property</kbd> viewer







---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L634"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `current_profit`

```python
current_profit()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L627"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `new`

```python
new(ledger: Ledger)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L590"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print`

```python
print(width=None)
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L638"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TrialBalance`
Trial balance is a dictionary of account names and their debit-side and credit-side balances. 


---

#### <kbd>property</kbd> viewer







---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L642"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `new`

```python
new(ledger: Ledger)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L590"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print`

```python
print(width=None)
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L663"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `CompoundEntry`
An entry that affects several accounts at once. 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(debits: list[tuple[str, int]], credits: list[tuple[str, int]]) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L694"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `from_balances`

```python
from_balances(chart: Chart, balances: AccountBalances) → CompoundEntry
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L680"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `to_entries`

```python
to_entries(null_account_name: str) → list[Entry]
```

Return list of double entries that make up multiple entry. The double entries will correspond to null account. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/core.py#L673"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `validate`

```python
validate()
```

Assert sum of debit entries equals sum of credit entries. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
