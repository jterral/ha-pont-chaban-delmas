# Tools
PYTHON ?= $(shell command -v python3)
PYTEST ?= $(shell command -v pytest)
RUFF ?= $(shell command -v ruff)


# ******************************************************************
##@ Python Tools

--python-check:
	@if [ -z "$(PYTHON)" ]; then echo "$(COLOR_RED)❌ python not found. Please install it.$(COLOR_RESET)"; exit 1; fi

.PHONY: python-venv
python-venv: --python-check  ## Configure Python virtual environment
	@printf "$(COLOR_CYAN)>> Configuring Python virtual environment...$(COLOR_RESET)\n"
	@$(PYTHON) -m venv .venv
	@.venv/bin/pip install -e ".[dev]"

.PHONY: python-test
python-test: --python-check  ## Run Python tests
	@printf "$(COLOR_CYAN)>> Running Python tests...$(COLOR_RESET)\n"
	@$(PYTHON) -m pytest tests/ -v

.PHONY: python-test-coverage
python-test-coverage: --python-check  ## Run Python tests with coverage
	@printf "$(COLOR_CYAN)>> Running Python tests with coverage...$(COLOR_RESET)\n"
	@$(PYTHON) -m pytest tests/ --cov=custom_components/pont_chaban_delmas --cov-report=term-missing --cov-report=html

.PHONY: python-lint
python-lint:  ## Run Python linter (ruff)
	@printf "$(COLOR_CYAN)>> Running Python linter...$(COLOR_RESET)\n"
	@$(PYTHON) -m ruff check custom_components/ tests/

.PHONY: python-format
python-format:  ## Format Python code (ruff)
	@printf "$(COLOR_CYAN)>> Formatting Python code...$(COLOR_RESET)\n"
	@$(PYTHON) -m ruff format custom_components/ tests/
