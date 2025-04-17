SRC_DIR = ../../

TESTS = \
	test_varequirementreader.py

.PHONY : \
	check \
	unit

unit: ${TESTS}
	PYTHONPATH=${SRC_DIR} python3 -m pytest ${TESTS} -vv

check: unit