.PHONY: help setup run validate clean tree stack-up stack-down stack-logs stack-check

ifeq ($(OS),Windows_NT)
PYTHON := python
VENV_BIN := .venv/Scripts
else
PYTHON := python3
VENV_BIN := .venv/bin
endif

VENV_PY := $(VENV_BIN)/python

help:
	@echo "Available targets:"
	@echo "  make setup     Create .venv and install requirements"
	@echo "  make run       Run the PySpark ETL demo"
	@echo "  make validate  Run the demo validation"
	@echo "  make clean     Remove generated output and Python caches"
	@echo "  make tree      Show files up to depth 3"
	@echo "  make stack-up    Start PostgreSQL and MinIO with Docker Compose"
	@echo "  make stack-down  Stop the Docker Compose stack"
	@echo "  make stack-logs  Show recent Docker Compose logs"
	@echo "  make stack-check Check Docker stack health"

setup:
	$(PYTHON) -m venv .venv
	$(VENV_PY) -m pip install --upgrade pip
	$(VENV_PY) -m pip install -r requirements.txt

run:
	$(VENV_PY) jobs/orders_etl.py

validate: run

clean:
	$(PYTHON) -c "import pathlib, shutil; shutil.rmtree('data/output/orders_by_category_parquet', ignore_errors=True); [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [p.unlink() for p in pathlib.Path('.').rglob('*.pyc') if p.is_file()]"

tree:
	$(PYTHON) -c "from pathlib import Path; root=Path('.'); ignored={'.git','.venv'}; paths=sorted(p for p in root.rglob('*') if not any(part in ignored for part in p.parts) and len(p.relative_to(root).parts)<=3); [print(str(p).replace(chr(92),'/') + ('/' if p.is_dir() else '')) for p in paths]"

stack-up:
	docker compose up -d

stack-down:
	docker compose down

stack-logs:
	docker compose logs --tail=100

stack-check:
	scripts/check_stack.sh
