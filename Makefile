# Colors
COLOR_RESET	:= \033[0m
COLOR_CYAN	:= \033[1;36m
COLOR_RED	:= \033[0;31m
COLOR_GREEN	:= \033[0;32m


.DEFAULT_GOAL := help

# ******************************************************************
##@ General

.PHONY: help
help:  ## Display this help
	@clear
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[3mcommand \033[0m \n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


include make/precommit.mk
include make/python.mk
