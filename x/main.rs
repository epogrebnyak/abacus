#[derive(Debug)]
enum RegularAccount {
    Asset(String),
    Expense(String),
    Capital(String),
    Liability(String),
    Income(String),
}

// Contra account
// Debit/Credit account ledger
// Rules for closing accounts
// Reporting results  

fn main() {
    println!("Hello, world!");
    let a1: RegularAccount = RegularAccount::Asset(String::from("cash"));
    println!("{:?}", a1);
}