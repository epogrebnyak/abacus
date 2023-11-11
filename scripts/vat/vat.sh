cx unlink --yes
cx init
abacus chart add --asset cash
abacus chart add --income sales
abacus chart add --liability vat
abacus ledger post-compound --debit cash 120 --credit sales 100 --credit vat 20
abacus report trial-balance
