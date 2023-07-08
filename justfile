package := "abacus"
readme_command := if os_family() == "windows" { "readme-console-win" } else { "readme-console-linux" }
# use cmd.exe instead of sh
set shell := ["cmd.exe", "/c"]


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
  just test-bat


# Run pytest (up to first error) and print slowest test times 
test:
  poetry run pytest -x --durations=5

test-bat:
  cd demo && call chart.bat
  cd demo && call operations.bat
  cd demo && call ledger.bat
  cd demo && call show.bat
  cd tests && call small.bat

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
  rm -f cli-example/chart.json cli-example/entries.json
  cat README.md | npx codedown bash > cli-example/minimal.sh
  just {{ readme_command }}

# Run console examples from README.md (Windows):
readme-console-win:
  cat cli-example/minimal.sh | python cli-example/call.py > cli-example/minimal.bat
  cd cli-example && poetry run call minimal.bat

# Run console examples from README.md (Linux):
readme-console-linux:
  poetry run bash -c "cd cli-example && source minimal.sh"

# Run Python code from README.md
readme-py:
  cat README.md | npx codedown python > cli-example/minimal.py
  poetry run python cli-example/minimal.py
  

# Build and serve docs
docs:
  poetry run mkdocs serve 

# Publish docs
docs-publish:
  poetry run mkdocs gh-deploy 

# Launch streamlit app (not in use)
app:
  poetry run streamlit run app/app.py
