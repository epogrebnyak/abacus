# Release target: 0.5.0 CLI app

Done:

- [ ] change multiple entry and start_balances
- [ ] `balances` and `--file`
- [ ] `chart list` must use .names dict

Doing:

- [ ] `ledger list` must show nicer output
- [ ] maybe less cli testing

Unsure about:

- init command
- entries may be separate file, not book
- if we have book, why need chart.json?

Wont fix:
- [ ] --title for entry
- [ ] testing of a multiline string `pytest-console-plugin`
- [ ] golden tests
- [ ] configuration: write to abacus.toml
- [ ] write to and read from Excel file
- [ ] colored output with --rich flag
- [ ] --assets --current --non-current
- [ ] --cash
