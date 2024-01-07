abacus extra unlink --yes
abacus init
abacus add asset:cash 
abacus add income:sales 
abacus add liability:vat --title "VAT payable"
abacus post-compound --debit cash 120 --credit sales 100 --credit vat 20
abacus report --all