<!-- markdownlint-disable -->

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/ledger.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `typer_cli.ledger`





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/ledger.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `assure_ledger_file_exists`

```python
assure_ledger_file_exists(store_file)
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/ledger.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `init`

```python
init()
```

Initialize ledger file in current directory. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/ledger.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `load`

```python
load(
    file: Path,
    chart_file: Optional[Path] = None,
    store_file: Optional[Path] = None
)
```

Load starting balances to ledger from JSON file. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/ledger.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `post`

```python
post(
    debit: str,
    credit: str,
    amount: int,
    title: Optional[str] = None,
    chart_file: Optional[Path] = None,
    store_file: Optional[Path] = None
)
```

Post double entry. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/ledger.py#L80"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `show`

```python
show(store_file: Optional[Path] = None)
```

Show ledger. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/ledger.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `unlink`

```python
unlink(yes: Annotated[bool, <OptionInfo object at 0x7f9e25c62a10>])
```

Permanently delete ledger file in current directory. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
