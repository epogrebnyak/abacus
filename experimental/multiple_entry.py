# def to_multiple_entry(ledger: Ledger, starting_balances: dict) -> MultipleEntry:
#     debit_entries = []
#     credit_entries = []
#     for account_name in starting_balances.keys():
#         try:
#             ledger[account_name]
#         except KeyError:
#             raise AbacusError(f"Account {account_name} does not exist in ledger.")
#     for account_name, amount in starting_balances.items():
#         match ledger[account_name]:
#             case DebitAccount(_, _):
#                 debit_entries.append((account_name, amount))
#             case CreditAccount(_, _):
#                 credit_entries.append((account_name, amount))
#     return MultipleEntry(debit_entries, credit_entries).validate()
