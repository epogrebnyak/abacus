# Motivation

## Original intent

`abacus` started as a project to demonstrate principles of double-entry accounting
through Python code, in spirit of [build-your-own-x](https://github.com/codecrafters-io/build-your-own-x).

## Teaching

You can use `abacus` to teach basics of accounting and accounting information systems (AIS),
or as a project in your Python class.

### Other uses

- Use `abacus` as a software component with other open source tools such as `medici` ledger.
- Convert reports between charts of accounts, for example local accounting standards to IFRS.
- Process business events in scenario simulations and make financial reports.
- Generate prompts for a large language model in accounting (RAG).

## DSL

The big goal for `abacus` is to become a DSL (domain-specific language)
for accounting, a notation system that allows to formulate accounting operations
in _'debit this — credit that'_ style and to demonstrate the results
of these operations as trail balance or financial statements.
This system would be independent of a specific ERP or book-keeping software vendor.
