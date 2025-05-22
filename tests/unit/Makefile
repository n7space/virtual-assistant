SRC_DIR = ../../
PYTHON ?= python3

TESTS = \
	test_vaqueries.py \
	test_varequirementreader.py \
	test_vaknowledgelibrary.py \
	test_vaengine.py \
	test_vallminterface.py

.PHONY : \
	check \
	unit

unit: ${TESTS}
	PYTHONPATH=${SRC_DIR} ${PYTHON} -m pytest ${TESTS} -vv

check: unit