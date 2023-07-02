# Release target: 0.5.0 CLI app

Done:

- [ ] change multiple entry and start_balances
- [ ] `balances` and `--file`

Doing:

- [ ] shift all chart test to chart.py
- [ ] `ledger list` must show nicer output
- [ ] `chart list` must use .names dict
- [ ] maybe less cli testing
- [ ] show vs report commands
- [ ] --title for entry

Unsure about:

- init command
- entries may be sepearate file, not book
- if we have book, why need chart.json?

Wont fix:

- [ ] testing of a multiline string `pytest-console-plugin`
- [ ] golden tests
- [ ] configuration: write to abacus.toml
- [ ] write to and read from Excel file
- [ ] colored output with --rich flag
- [ ] --assets --current --non-current
- [ ] --cash
