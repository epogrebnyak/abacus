# What's inside?

## `abacus.core`

`abacus.core` is responsible for the main pipeline of data transformation
in `abacus`, namely defining a chart of accounts, creating a ledger based
on the chart, adding accounting entries, closing accounts and producing reports.

A simplified view of the pipeline is:

`Chart -> Ledger -> [Entry] -> Ledger -> Report`

## `abacus.user_chart`

The user input goes first to `UserChart` that can be saved to JSON file
(chart.json), then converted to converted to `Chart`.

## `abacus.entries_store`

`abacus` uses `jsonlist` format for storing entries.
The file name is `entries.jsonlist`.

## `abacus.show` and `abacus.show_rich`

These modules allow printing of reports to console.
