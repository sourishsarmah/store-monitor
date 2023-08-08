.PHONY: venv install-deps format lint start

ifneq (,$(wildcard ./.env))
    include .env
    export
endif

VENV=../venv
INSTALL_DEV=true
PYTHON=$(VENV)/bin/python3

venv:
	python3 -m pip install --upgrade pip setuptools wheel
	python3 -m venv $(VENV)

install-deps:  ## Install dependencies
	python3 -m pip install poetry
	poetry install

format:
	set -x
	isort --recursive  --force-single-line-imports --apply app
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app --exclude=__init__.py
	black app
	isort --recursive --apply app

test:
	set -e
	set -x
	pytest --cov=app --cov-report=term-missing app/tests

lint: 
	set -x
	mypy app
	black app --check
	isort --recursive --check-only app
	flake8

start:  ## Run application server in development
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload