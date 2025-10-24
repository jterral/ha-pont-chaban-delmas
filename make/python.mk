# Tools
PYTHON ?= $(shell command -v python3)


# ******************************************************************
##@ Python Tools

--python-check:
	@if [ -z "$(PYTHON)" ]; then echo "$(COLOR_RED)❌ python not found. Please install it.$(COLOR_RESET)"; exit 1; fi

.PHONY: python-venv
python-venv: --python-check  ## Configure Python virtual environment
	@printf "$(COLOR_CYAN)>> Configuring Python virtual environment...$(COLOR_RESET)\n"
	@$(PYTHON) -m venv .venv
	@.venv/bin/pip install -r requirements.txt
