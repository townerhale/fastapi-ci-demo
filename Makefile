# Makefile — common developer commands
# Usage:
#   make install
#   make test
#   make docker-build
#   make run

SHELL := /bin/bash

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

IMAGE := circleci-field-app

.PHONY: install test docker-build run

## Create a Python virtual environment and install dependencies
install:
@set -euo pipefail; \
if [ ! -d "$(VENV)" ]; then \
python3 -m venv "$(VENV)"; \
fi; \
"$(PIP)" install -U pip; \
"$(PIP)" install -r requirements.txt; \
echo "✅ Dependencies installed into $(VENV)"

## Run pytest with coverage (uses pytest.ini)
test:
@set -euo pipefail; \
if [ ! -x "$(PYTEST)" ]; then \
$(MAKE) install; \
fi; \
"$(PYTEST)"

## Build the Docker image
docker-build:
@set -euo pipefail; \
docker build -t "$(IMAGE)" .

## Run the application locally via run.py
run:
@set -euo pipefail; \
if [ ! -x "$(PYTHON)" ]; then \
$(MAKE) install; \
fi; \
"$(PYTHON)" run.py
