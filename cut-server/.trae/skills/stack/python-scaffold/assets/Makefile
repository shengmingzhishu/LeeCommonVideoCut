.PHONY: install test lint format clean run help

PYTHON_BIN := .venv/bin/python
PIP_BIN := .venv/bin/pip

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies into a virtualenv
	python -m venv .venv
	$(PIP_BIN) install --upgrade pip
	$(PIP_BIN) install -r requirements.txt
	$(PIP_BIN) install -e .

test: ## Run tests
	$(PYTHON_BIN) -m pytest tests/ --cov={{ project_name }}

lint: ## Run linting checks
	$(PYTHON_BIN) -m mypy {{ project_name }}
	$(PYTHON_BIN) -m black --check {{ project_name }}
	$(PYTHON_BIN) -m isort --check {{ project_name }}

format: ## Format code
	$(PYTHON_BIN) -m black {{ project_name }}
	$(PYTHON_BIN) -m isort {{ project_name }}

run: ## Run the application
	$(PYTHON_BIN) -m {{ project_name }}.main

clean: ## Clean temporary files
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf dist build *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
