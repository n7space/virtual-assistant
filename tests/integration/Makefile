SRC_DIR = ../../
PYTHON ?= python3

TESTS = \
	test_restapi.py

.PHONY : \
	check \
	integration

integration: ${TESTS}
	PYTHONPATH=${SRC_DIR} ${PYTHON} -m pytest ${TESTS} -vv

check: integration