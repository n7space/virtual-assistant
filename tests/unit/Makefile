SRC_DIR = ../../
PYTHON ?= python

TESTS = \
	test_varequirementreader.py \
	test_vallminterface.py

.PHONY : \
	check \
	unit

unit: ${TESTS}
	PYTHONPATH=${SRC_DIR} ${PYTHON} -m pytest ${TESTS} -vv

check: unit