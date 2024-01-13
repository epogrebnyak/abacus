<!-- markdownlint-disable -->

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/app.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `typer_cli.app`
Typer app, including Click subcommand. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/app.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `callback`

```python
callback()
```

Typer app, including Click subapp 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/app.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `init`

```python
init()
```

Initialize project files in current folder. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/app.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `assert_`

```python
assert_(
    name: str,
    balance: int,
    chart_file: Optional[Path] = None,
    ledger_file: Optional[Path] = None
)
```

Verify account balance. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/app.py#L62"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `close`

```python
close()
```

Close accounts at period end. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/app.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `report`

```python
report(
    balance_sheet: Annotated[bool, <OptionInfo object at 0x7f9e25c7b6a0>] = False,
    income_statement: Annotated[bool, <OptionInfo object at 0x7f9e25c7b7f0>] = False,
    trial_balance: Annotated[bool, <OptionInfo object at 0x7f9e25c79420>] = False,
    all_reports: Annotated[bool, <OptionInfo object at 0x7f9e25c797b0>] = False,
    json: bool = False
)
```

Show reports. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/app.py#L117"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `unlink`

```python
unlink(yes: Annotated[bool, <OptionInfo object at 0x7f9e25c7b730>])
```

Permanently delete project files in current directory. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
