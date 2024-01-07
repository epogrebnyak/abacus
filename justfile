package := "abacus"
readme_command := if os_family() == "windows" { "readme-console-win" } else { "readme-console-linux" }
source_command := if os_family() == "windows" { "call" } else { "source" }
#use cmd.exe instead of sh on Window
set shell := ["cmd.exe", "/c"]


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
  just scripts

# Run examples 
scripts:
  poetry run python readme.py
  rm chart.json && rm entries.linejson && readme.bat
  cd scripts/vat && vat.bat
  just docs-py
  just docs-cli

#  cd scripts/abacus && bash -e all.sh
#  cd scripts/cx && bash -e joan.sh
#  cd scripts/vat && bash -e vat.sh
#cli:
#  cd scripts/abacus && bash -e all.sh 

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

# Run Python code from docs
docs-py:
  poetry run python docs/echo.py docs/quick_start.md | npx codedown python > docs/quick_start.py
  poetry run python docs/quick_start.py
  poetry run python docs/echo.py docs/index.md | npx codedown python > docs/index.py
  poetry run python docs/index.py


# Run console examples from docs
docs-cli:
  poetry run python docs/echo.py docs/quick_start.md | npx codedown bash > docs/quick_start.bat
  cd docs && rm -f chart.json entries.linejson && quick_start.bat
  poetry run python docs/echo.py docs/index.md | npx codedown bash > docs/index.bat
  cd docs && rm -f chart.json entries.linejson && index.bat



# Build and serve docs
docs:
  poetry run mkdocs serve 

# Publish docs
docs-publish:
  poetry run mkdocs gh-deploy 

# Publish to PyPI
publish:
  poetry publish --build

patch:
  poetry version patch
