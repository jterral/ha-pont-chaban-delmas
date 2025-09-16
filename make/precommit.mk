# Tools
PIP ?= $(shell command -v pip)
PRECOMMIT ?= $(shell command -v pre-commit)


# ******************************************************************
##@ Precommit Tools

--precommit-check:
	@if [ -z "$(PRECOMMIT)" ]; then echo "$(COLOR_RED)❌ pre-commit not found. Please install it.$(COLOR_RESET)"; exit 1; fi

.PHONY: precommit-install
precommit-install:  ## Install precommit executable
	@printf "$(COLOR_CYAN)>> Installing pre-commit executable...$(COLOR_RESET)\n"
	@$(PIP) install pre-commit --break-system-packages

.PHONY: precommit-configure
precommit-configure: --precommit-check  ## Configure precommit hooks
	@printf "$(COLOR_CYAN)>> Configuring Git hooks for pre-commit, commit-msg, and pre-push...$(COLOR_RESET)\n"
	@$(PRECOMMIT) install --install-hooks
	@$(PRECOMMIT) install --hook-type commit-msg
	@$(PRECOMMIT) install --hook-type pre-push

.PHONY: precommit-update
precommit-update: --precommit-check  ## Update precommit hooks
	@printf "$(COLOR_CYAN)>> Updating pre-commit hooks to latest versions...$(COLOR_RESET)\n"
	@$(PRECOMMIT) autoupdate

.PHONY: precommit-remove
precommit-remove: --precommit-check  ## Remove all precommit hooks
	@printf "$(COLOR_CYAN)>> Removing all Git hooks and pre-commit configurations...$(COLOR_RESET)\n"
	@$(PRECOMMIT) remove -t pre-commit -t pre-merge-commit -t pre-push -t prepare-commit-msg -t commit-msg -t post-commit -t post-checkout -t post-merge -t post-rewrite

.PHONY: precommit
precommit: --precommit-check  ## Run all precommit checks
	@printf "$(COLOR_CYAN)>> Running pre-commit checks...$(COLOR_RESET)\n"
	@$(PRECOMMIT) run --all-files

.PHONY: precommit-run
precommit-run: --precommit-check  ## Run precommit hook
	@if [ "${hook}" = "" ]; then\
		printf "$(COLOR_RED)'hook' parameter is empty$(COLOR_RESET)\n";\
		printf "$(COLOR_YELLOW)make precommit-run hook=<hook-name>$(COLOR_RESET)\n";\
		exit 1;\
	fi
	@printf "$(COLOR_CYAN)>> Running pre-commit hook '$(hook)'...$(COLOR_RESET)\n"
	@$(PRECOMMIT) run --all-files $(hook)
