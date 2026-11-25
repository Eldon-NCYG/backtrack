PY := .venv/bin/python
DBT := cd transform && ../.venv/bin/dbt

.PHONY: setup fake load build test lint all docs clean

setup:  ## create the virtualenv and install everything
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e ".[dev]"

fake:   ## generate a fake export in data/export/ (for development and CI)
	$(PY) -m ingestion.fake_export --out data/export --plays 5000

load:   ## load the export into the warehouse (safe to re-run)
	$(PY) -m ingestion.load_export

build:  ## run and test every dbt model
	$(DBT) build --profiles-dir .

test:   ## run pytest
	$(PY) -m pytest -q

lint:   ## run ruff
	.venv/bin/ruff check .

docs:   ## generate and serve dbt docs (lineage + schema)
	$(DBT) docs generate --profiles-dir . && $(DBT) docs serve --profiles-dir .

all: load build

clean:  ## remove the local warehouse and raw zone (keeps your export)
	rm -rf data/raw data/listening.duckdb transform/target
