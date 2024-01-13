bx chart unlink --yes
bx chart init 
bx chart add -a cash ar paper
bx chart add -c equity
bx chart add --liability loan 
bx chart add income:sales expense:salaries,interest
bx chart add contra:equity:ts --title "Treasury stock"
bx chart name paper "Inventory (paper products)"
bx chart offset sales refunds voids
bx chart set --retained-earnings-account new_isa --income-summary-account new_re --null-account new_null
bx chart show
bx ledger unlink --yes
bx ledger init
bx post --entry asset:cash capital:equity 1000