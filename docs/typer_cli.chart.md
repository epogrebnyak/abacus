<!-- markdownlint-disable -->

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/chart.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `typer_cli.chart`





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/chart.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `assure_chart_file_exists`

```python
assure_chart_file_exists(chart_file=None)
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/chart.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `init`

```python
init()
```

Initialize chart file in current directory. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/chart.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `spaced`

```python
spaced(labels: list[str]) → str
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/chart.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `add`

```python
add(
    labels: List[str],
    asset: Annotated[bool, <OptionInfo object at 0x7f9e25c61390>] = False,
    capital: Annotated[bool, <OptionInfo object at 0x7f9e25c62860>] = False,
    liability: Annotated[bool, <OptionInfo object at 0x7f9e25c61c30>] = False,
    income: Annotated[bool, <OptionInfo object at 0x7f9e25c63460>] = False,
    expense: Annotated[bool, <OptionInfo object at 0x7f9e25c62e00>] = False,
    title: Annotated[Optional[str], <OptionInfo object at 0x7f9e25c61450>] = None,
    chart_file: Optional[Path] = None
)
```

Add accounts to chart. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/chart.py#L88"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `set`

```python
set(
    income_summary_account: Optional[str] = None,
    retained_earnings_account: Optional[str] = None,
    null_account: Optional[str] = None,
    chart_file: Optional[Path] = None
)
```

Set income summary, retained earnings or null accounts. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/chart.py#L111"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `name`

```python
name(account_name: str, title: str, chart_file: Optional[Path] = None)
```

Set account title. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/chart.py#L119"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `offset`

```python
offset(name: str, contra_names: list[str], chart_file: Optional[Path] = None)
```

Add contra accounts. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/chart.py#L133"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `show`

```python
show(chart_file: Optional[Path] = None)
```

Print chart. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/typer_cli/chart.py#L140"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `unlink`

```python
unlink(yes: Annotated[bool, <OptionInfo object at 0x7f9e25c60460>])
```

Permanently delete chart file in current directory. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
