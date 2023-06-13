# Chart of accounts

Chart of accounts (CAO) is a list of accounts to be used by a company.
Chart of accounts may be defined by the government (in Europe)
or can be specified by the company itself according to guidelines (in the US).
Fiscal rules and reporting requirements also affect composition of a chart of accounts.

Charts of accounts are not that easy to find in an open, structured and machine-readable format.
They usually exist as a published PDF document (sometimes an Excel file)
or may be deeply embedded in accounting software, either open source (like Odoo)
or proprietary (Oracle, SAP, NetSuite, Xero or QuickBooks).
[Odoo][odoo] is specific has a list of localisations for many countries.

[odoo]: https://www.odoo.com/documentation/16.0/applications/finance/fiscal_localizations.html

A few selected charts are below:

- IFRS reference chart (similar to [this](https://www.ifrs-gaap.com/ifrs-chart-accounts))
- [BAS (Sweden)](https://www.bas.se/english/chart-of-account/)
- [SKR03 and SKR04 (Germany)](https://github.com/Dolibarr/dolibarr/issues/22363)
- [PCMN (Belgium)](https://www.cnc-cbn.be/fr/node/2250/multilingual-comparison/en)
- [RAS (Russia)](https://minfin.gov.ru/ru/document/?id_4=2293-plan_schetov_bukhgalterskogo_ucheta_finansovo-khozyaistvennoi_dyeyatelnosti_organizatsii_i_instruktsiya_po_primeneniyu_plana_schetov_bukhgalterskogo_ucheta_finansovo-khozyaistv)

There are also textbook charts and sample charts like [Dunder Muffin Paper Company][yv8bkm] fun chart.

[yv8bkm]: https://www.reddit.com/r/DunderMifflin/comments/yv8bkm/the_office_chart_of_accounts

`abacus` allows to create and maintain charts of accounts as JSON files.
After a chart is specified, one can post entries and create financial reports.
Migration between domestic and IFRS-compatible charts considered for `abacus`, but not implemented yet (see [issue #4][4]).

[4]: https://github.com/epogrebnyak/abacus/issues/4
