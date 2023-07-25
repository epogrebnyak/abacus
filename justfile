package := "abacus"
readme_command := if os_family() == "windows" { "readme-console-win" } else { "readme-console-linux" }
# use cmd.exe instead of sh
# set shell := ["cmd.exe", "/c"]


# List all commands
list:
  just --list 

# Run all tests, checks and linters
grill:
  just test
  just mypy
  just isort
  just black
  just ruff
  just md
  just readme

# Run pytest (up to first error) and print slowest test times 
test:
  poetry run pytest -x --durations=5

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

# Run console examples from README.md
readme-console:
  cat README.md | npx codedown bash > examples/readme/minimal.sh
  rm -rf examples/readme/try_abacus
  just {{ readme_command }}

# Run console examples from README.md (Windows):
readme-console-win:
  cp examples/readme/minimal.sh examples/readme/minimal.bat
  cd examples/readme && call minimal.bat
  jsut test-bat

# Run console examples from README.md (Linux):
readme-console-linux:
  poetry run bash -c "cd examples/readme && source minimal.sh"

# Demo command line example and test_cli.bat (Windows)
test-bat:
  cd examples/demo && call chart.bat
  cd examples/demo && call operations.bat
  cd examples/demo && call ledger.bat
  cd examples/demo && call show.bat
  cd tests && call test_cli.bat


# Run Python code from README.md
readme-py:
  cat README.md | npx codedown python > examples/readme/minimal.py
  poetry run python examples/readme/minimal.py
  
# Build and serve docs
docs:
  poetry run mkdocs serve 

# Publish docs
docs-publish:
  poetry run mkdocs gh-deploy 

# Launch streamlit app (not in use)
app:
  poetry run streamlit run app/app.py
