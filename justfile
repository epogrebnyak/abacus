package := "abacus"
readme_command := if os_family() == "windows" { "readme-console-win" } else { "readme-console-linux" }
source_command := if os_family() == "windows" { "call" } else { "source" }
# use cmd.exe instead of sh
# set shell := ["cmd.exe", "/c"]


# List all commands
list:
  just --list 

# Run key tests
go:
  just test
  just mypy
  just isort
  just black
  just ruff

# Run all tests, checks and linters
grill:
  just go
  just md
  just readme
  just scripts

# Run pytest (up to first error) and print slowest test times 
test:
  poetry run pytest . -x --durations=5


# Type check
mypy:
  poetry run mypy {{ package }}

# Run isort (black-compatible and float imports to top)
isort:
  poetry run isort --profile black --float-to-top .

# Run black
black:  
  poetry run black .

# Apply ruff
ruff:
  poetry run ruff check . --fix

# Prettify markdown files (use .prettierignore to exclude files)
md:
  npx prettier . --write

# Run Python code and console commands from README.md 
readme:  
  just readme-py
  just readme-console

# Run Python code from README.md
readme-py:
  cat README.md | npx codedown python > scripts/minimal.py
  poetry run python scripts/minimal.py

# Run console examples from README.md
readme-console:
  cat README.md | npx codedown bash > scripts/minimal.sh
  rm -f scripts/chart.json scripts/entries.csv
  cd scripts && bash -e minimal.sh

# Run command line examples (Linux)
scripts:
  cd scripts && bash -e all.sh
 
# Build and serve docs
docs:
  poetry run mkdocs serve 

# Publish docs
docs-publish:
  poetry run mkdocs gh-deploy 
