<!-- markdownlint-disable -->

# API Overview

## Modules

- [`base`](./base.md#module-base): Base classes (may helps to prevent circular import).
- [`cli`](./cli.md#module-cli)
- [`core`](./core.md#module-core): Core elements of a minimal double-entry accounting system.
- [`entries_store`](./entries_store.md#module-entries_store): Write and read accounting entries from a file.
- [`typer_cli`](./typer_cli.md#module-typer_cli)
- [`typer_cli.app`](./typer_cli.app.md#module-typer_cliapp): Typer app, including Click subcommand.
- [`typer_cli.base`](./typer_cli.base.md#module-typer_clibase): Navigation for CLI.
- [`typer_cli.chart`](./typer_cli.chart.md#module-typer_clichart)
- [`typer_cli.ledger`](./typer_cli.ledger.md#module-typer_cliledger)
- [`typer_cli.post`](./typer_cli.post.md#module-typer_clipost): Post entries to ledger.
- [`typer_cli.show`](./typer_cli.show.md#module-typer_clishow)
- [`user_chart`](./user_chart.md#module-user_chart): User-defined chart of accounts.
- [`viewers`](./viewers.md#module-viewers): Viewers for trial balance, income statement, balance sheet reports.

## Classes

- [`base.AbacusError`](./base.md#class-abacuserror): Custom error for this project.
- [`core.Account`](./core.md#class-account): Account(name: str, contra_accounts: list[str] = <factory>)
- [`core.AccountBalances`](./core.md#class-accountbalances)
- [`core.Asset`](./core.md#class-asset)
- [`core.BalanceSheet`](./core.md#class-balancesheet): BalanceSheet(assets: core.AccountBalances, capital: core.AccountBalances, liabilities: core.AccountBalances)
- [`core.Capital`](./core.md#class-capital)
- [`core.Chart`](./core.md#class-chart): Chart of accounts.
- [`core.CompoundEntry`](./core.md#class-compoundentry): An entry that affects several accounts at once.
- [`core.Contra`](./core.md#class-contra): Contra(t: core.T)
- [`core.ContraAccount`](./core.md#class-contraaccount)
- [`core.ContraAsset`](./core.md#class-contraasset)
- [`core.ContraCapital`](./core.md#class-contracapital)
- [`core.ContraExpense`](./core.md#class-contraexpense)
- [`core.ContraIncome`](./core.md#class-contraincome)
- [`core.ContraLiability`](./core.md#class-contraliability)
- [`core.CreditAccount`](./core.md#class-creditaccount)
- [`core.DebitAccount`](./core.md#class-debitaccount)
- [`core.Entry`](./core.md#class-entry): Double entry with account name to be debited,
- [`core.Expense`](./core.md#class-expense)
- [`core.ExtraAccount`](./core.md#class-extraaccount)
- [`core.ExtraCreditAccount`](./core.md#class-extracreditaccount)
- [`core.ExtraDebitAccount`](./core.md#class-extradebitaccount)
- [`core.Holder`](./core.md#class-holder): The `Holder` class is a wrapper to hold an account type
- [`core.Income`](./core.md#class-income)
- [`core.IncomeStatement`](./core.md#class-incomestatement): IncomeStatement(income: core.AccountBalances, expenses: core.AccountBalances)
- [`core.IncomeSummaryAccount`](./core.md#class-incomesummaryaccount)
- [`core.Ledger`](./core.md#class-ledger)
- [`core.Liability`](./core.md#class-liability)
- [`core.NullAccount`](./core.md#class-nullaccount)
- [`core.Pipeline`](./core.md#class-pipeline): A pipeline to accumulate ledger transformations.
- [`core.Regular`](./core.md#class-regular): Regular(t: core.T)
- [`core.RegularAccount`](./core.md#class-regularaccount)
- [`core.Report`](./core.md#class-report): Report(chart: core.Chart, ledger: core.Ledger, rename_dict: dict[str, str] = <factory>)
- [`core.Statement`](./core.md#class-statement)
- [`core.T`](./core.md#class-t): Five types of accounts and standard prefixes for account names.
- [`core.TAccount`](./core.md#class-taccount): T-account will hold amounts on debits and credit side.
- [`core.TrialBalance`](./core.md#class-trialbalance): Trial balance is a dictionary of account names and
- [`core.Wrap`](./core.md#class-wrap): Holder for accounts that do not belong to any of 5 account types.
- [`entries_store.LineJSON`](./entries_store.md#class-linejson): LineJSON(path: pathlib.Path)
- [`user_chart.AccountLabel`](./user_chart.md#class-accountlabel): AccountLabel(type: abacus.core.T, contra_names: list[str] = <factory>)
- [`user_chart.Composer`](./user_chart.md#class-composer): Composer(contra: str = 'contra', translation: dict[str, str] = <factory>)
- [`user_chart.Label`](./user_chart.md#class-label): Label(t: abacus.core.T, name: str)
- [`user_chart.Offset`](./user_chart.md#class-offset): Offset(name: str, contra_name: str)
- [`user_chart.UserChart`](./user_chart.md#class-userchart)
- [`viewers.BalanceSheetViewer`](./viewers.md#class-balancesheetviewer): BalanceSheetViewer(statement: abacus.core.BalanceSheet, title: str = 'Balance sheet', rename_dict: dict[str, str] = <factory>)
- [`viewers.BoldF`](./viewers.md#class-boldf): BoldF()
- [`viewers.Cell`](./viewers.md#class-cell): Cell(content: viewers.String | viewers.Number, formats: list[viewers.Format] = <factory>)
- [`viewers.Format`](./viewers.md#class-format): Format()
- [`viewers.IncomeStatementViewer`](./viewers.md#class-incomestatementviewer): IncomeStatementViewer(statement: abacus.core.IncomeStatement, title: str = 'Income Statement', rename_dict: dict[str, str] = <factory>)
- [`viewers.Number`](./viewers.md#class-number): Number(n: int)
- [`viewers.OffsetF`](./viewers.md#class-offsetf): OffsetF()
- [`viewers.PairColumn`](./viewers.md#class-paircolumn): PairColumn(xs: list[viewers.Cell], ys: list[viewers.Cell])
- [`viewers.String`](./viewers.md#class-string): String(s: str)
- [`viewers.TextColumn`](./viewers.md#class-textcolumn): Column for creating tables.
- [`viewers.TrialBalanceViewer`](./viewers.md#class-trialbalanceviewer): TrialBalanceViewer(statement: dict[str, tuple[int, int]], rename_dict: dict[str, str] = <factory>, headers: tuple[str, str, str] = ('Account', 'Debit', 'Credit'), title: str = 'Trial balance')
- [`viewers.Viewer`](./viewers.md#class-viewer): Viewer()

## Functions

- [`cli.account_balances`](./cli.md#function-account_balances)
- [`cli.balance_sheet`](./cli.md#function-balance_sheet)
- [`cli.cwd`](./cli.md#function-cwd)
- [`cli.get_chart`](./cli.md#function-get_chart)
- [`cli.get_chart_path`](./cli.md#function-get_chart_path)
- [`cli.get_current_ledger`](./cli.md#function-get_current_ledger)
- [`cli.get_entries_path`](./cli.md#function-get_entries_path)
- [`cli.get_store`](./cli.md#function-get_store)
- [`cli.get_user_chart`](./cli.md#function-get_user_chart)
- [`cli.income_statement`](./cli.md#function-income_statement)
- [`cli.jsonify`](./cli.md#function-jsonify)
- [`cli.last`](./cli.md#function-last)
- [`cli.trial_balance`](./cli.md#function-trial_balance)
- [`core.contra_pairs`](./core.md#function-contra_pairs): Return list of account and contra account name pairs for a given type of contra account.
- [`core.starting_entries`](./core.md#function-starting_entries)
- [`core.sum_second`](./core.md#function-sum_second)
- [`app.assert_`](./typer_cli.app.md#function-assert_): Verify account balance.
- [`app.callback`](./typer_cli.app.md#function-callback): Typer app, including Click subapp
- [`app.close`](./typer_cli.app.md#function-close): Close accounts at period end.
- [`app.init`](./typer_cli.app.md#function-init): Initialize project files in current folder.
- [`app.report`](./typer_cli.app.md#function-report): Show reports.
- [`app.unlink`](./typer_cli.app.md#function-unlink): Permanently delete project files in current directory.
- [`base.get_chart`](./typer_cli.base.md#function-get_chart)
- [`base.get_ledger`](./typer_cli.base.md#function-get_ledger)
- [`base.get_ledger_income_statement`](./typer_cli.base.md#function-get_ledger_income_statement)
- [`base.get_store`](./typer_cli.base.md#function-get_store)
- [`base.last`](./typer_cli.base.md#function-last)
- [`chart.add`](./typer_cli.chart.md#function-add): Add accounts to chart.
- [`chart.assure_chart_file_exists`](./typer_cli.chart.md#function-assure_chart_file_exists)
- [`chart.init`](./typer_cli.chart.md#function-init): Initialize chart file in current directory.
- [`chart.name`](./typer_cli.chart.md#function-name): Set account title.
- [`chart.offset`](./typer_cli.chart.md#function-offset): Add contra accounts.
- [`chart.set`](./typer_cli.chart.md#function-set): Set income summary, retained earnings or null accounts.
- [`chart.show`](./typer_cli.chart.md#function-show): Print chart.
- [`chart.spaced`](./typer_cli.chart.md#function-spaced)
- [`chart.unlink`](./typer_cli.chart.md#function-unlink): Permanently delete chart file in current directory.
- [`ledger.assure_ledger_file_exists`](./typer_cli.ledger.md#function-assure_ledger_file_exists)
- [`ledger.init`](./typer_cli.ledger.md#function-init): Initialize ledger file in current directory.
- [`ledger.load`](./typer_cli.ledger.md#function-load): Load starting balances to ledger from JSON file.
- [`ledger.post`](./typer_cli.ledger.md#function-post): Post double entry.
- [`ledger.show`](./typer_cli.ledger.md#function-show): Show ledger.
- [`ledger.unlink`](./typer_cli.ledger.md#function-unlink): Permanently delete ledger file in current directory.
- [`post.post_compound`](./typer_cli.post.md#function-post_compound)
- [`show.account`](./typer_cli.show.md#function-account): Show account information.
- [`show.balances`](./typer_cli.show.md#function-balances): Show account balances.
- [`user_chart.AccountLabel.__init__`](./user_chart.md#function-__init__)
- [`user_chart.extract`](./user_chart.md#function-extract): Extract one or several account labels from an input string.
- [`user_chart.make_user_chart`](./user_chart.md#function-make_user_chart)
- [`viewers.bold`](./viewers.md#function-bold)
- [`viewers.equalize_length`](./viewers.md#function-equalize_length)
- [`viewers.maps`](./viewers.md#function-maps)
- [`viewers.print_viewers`](./viewers.md#function-print_viewers)
- [`viewers.red`](./viewers.md#function-red): Make digit red if negative.


---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
