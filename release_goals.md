# CLI app notes

- change readme
- consolidate at /example folder
- minor appearances of text
- `--reference` or `--refer`
- adjustment example (with trial balance)
- post-close example
- add operation title to entry title
- add small hash for entry
- `--cash` asset type
- `--current-asset`, `--non-current-asset` asset type
- `--current-liability`, `--long-term-liability`

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
- [ ] configuration: write to abacus.toml
- [ ] write to and read from Excel file
- [ ] colored output with --rich flag
- [ ] --assets --current --non-current
- [ ] --cash
