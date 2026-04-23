# Validation Makefile for Virtual Assistant Requirements

SHELL := /bin/bash
QUERY_DEFS := validation_queries.json
REQUIREMENTS := validation_requirements.xlsx

# Default target: run all validation tests
.PHONY: all
all: test-mbep-fun-1100 test-mbep-fun-1110 test-mbep-fun-1120 test-mbep-fun-1130 test-mbep-if-710

# MBEP-FUN-1100: Virtual Assistant shall be able to answer predefined queries about individual requirements.
.PHONY: test-mbep-fun-1100
test-mbep-fun-1100:
	@echo "========================================"
	@echo "Test: test-mbep-fun-1100"
	@echo "Requirement: MBEP-FUN-1100 - Virtual Assistant shall be able to answer predefined queries about individual requirements."
	@echo "========================================"
	vareq --mode query \
		--query-definitions-path $(QUERY_DEFS) \
		--query-definitions-base-directory . \
		--requirements $(REQUIREMENTS) \
		--query-id review \
		--requirement-id VAL-REQ-001

# MBEP-FUN-1110: Virtual Assistant shall be able to answer predefined queries about all requirements in the project.
.PHONY: test-mbep-fun-1110
test-mbep-fun-1110:
	@echo "========================================"
	@echo "Test: test-mbep-fun-1110"
	@echo "Requirement: MBEP-FUN-1110 - Virtual Assistant shall be able to answer predefined queries about all requirements in the project."
	@echo "========================================"
	vareq --mode query \
		--query-definitions-path $(QUERY_DEFS) \
		--query-definitions-base-directory . \
		--requirements $(REQUIREMENTS) \
		--query-id check-all

# MBEP-FUN-1120: Virtual Assistant shall be able to answer a free-form query about all requirements in the project.
.PHONY: test-mbep-fun-1120
test-mbep-fun-1120:
	@echo "========================================"
	@echo "Test: test-mbep-fun-1120"
	@echo "Requirement: MBEP-FUN-1120 - Virtual Assistant shall be able to answer a free-form query about all requirements in the project."
	@echo "========================================"
	@echo "Verifying chat mode is available..."
	vareq --help | grep -q "chat" && echo "PASS: Chat mode available for free-form queries"
	@echo "Invoking chat with a free-form question..."
	@echo -e "List all requirements and summarize them briefly.\n" | vareq --mode chat \
		--requirements $(REQUIREMENTS) \
		--verbosity error

# MBEP-FUN-1130: The Virtual Assistant shall be able to inform a user how to properly set it up.
.PHONY: test-mbep-fun-1130
test-mbep-fun-1130:
	@echo "========================================"
	@echo "Test: test-mbep-fun-1130"
	@echo "Requirement: MBEP-FUN-1130 - The Virtual Assistant shall be able to inform a user how to properly set it up."
	@echo "========================================"
	vareq --setup-instructions

# MBEP-IF-710: It shall be possible to access Virtual Assistant functionality from command line interface.
.PHONY: test-mbep-if-710
test-mbep-if-710:
	@echo "========================================"
	@echo "Test: test-mbep-if-710"
	@echo "Requirement: MBEP-IF-710 - It shall be possible to access Virtual Assistant functionality from command line interface."
	@echo "========================================"
	@which vareq && echo "PASS: vareq command found in PATH"
	vareq --help > /dev/null && echo "PASS: vareq --help executes successfully"

# Clean target
.PHONY: clean
clean:
	@echo "Nothing to clean"

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all                 - Run all validation tests"
	@echo "  test-mbep-fun-1100  - Test predefined queries on individual requirements"
	@echo "  test-mbep-fun-1110  - Test predefined queries on all requirements"
	@echo "  test-mbep-fun-1120  - Test free-form query capability"
	@echo "  test-mbep-fun-1130  - Test setup instructions"
	@echo "  test-mbep-if-710    - Test CLI accessibility"
	@echo "  clean               - Clean generated files"
	@echo "  help                - Show this help message"
