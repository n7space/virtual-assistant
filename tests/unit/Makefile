SRC_DIR = ../../
PYTHON ?= python3

TESTS = \
	test_varequirementreader.py \
	test_vaknowledgelibrary.py

.PHONY : \
	check \
	unit

unit: ${TESTS}
	PYTHONPATH=${SRC_DIR} ${PYTHON} -m pytest ${TESTS} -vv

check: unit