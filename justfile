package := "abacus"
command := if os_family() == "windows" { "poetry run minimal.bat" } else { "bash source ./minimal.sh" }

# run pytest
test:
  poetry run pytest

# run all tests and checks
grill:
  just test
  just mypy
  just ruff
  just readme-py
  just readme-console
  just isort
  just black
  just md

# run console examples from README.md (FIXME)
readme-console-win:
  cat README.md | npx codedown console > cli-example/minimal.sh
  cat cli-example/minimal.sh | python cli-example/call.py > cli-example/minimal.bat
  echo FIXME: Code below will create chart.json and store.json in root dicrectory,
  echo but want it in cli-example.
  cd cli-example & poetry run call "cli-example/minimal.bat"
  echo For example the command below will print just /abacus, not /abacus/cli-example
  cd cli-example & pwd
  echo We do not really know how to switch to a directory in just command runner 
  echo and make poetry understand the directory has changed.

# run console examples from README.md in linux (FIXME)
readme-console-linux:
  echo assume is already created cli-example/minimal.sh
  echo how can one make it run on linux?
  echo Tried command below, but no success (source not found)
  source ./cli-example/minimal.sh


# run Python code from README.md
readme-py:
  cat README.md | npx codedown python > cli-example/minimal.py
  poetry run python cli-example/minimal.py

# prettify markdown
md:
  npx prettier . --write

isort:
  poetry run isort --profile black --float-to-top .

# apply ruff linter
ruff:
  poetry run ruff check . --fix

# type check
mypy:
  poetry run mypy abacus

# use black and isort
black:  
  poetry run black .

# build and serve docs
docs:
  poetry run mkdocs serve 

# publish docs
docs-publish:
  poetry run mkdocs gh-deploy 

# launch streamlit app (depreciated)
app:
  poetry run streamlit run app/app.py
