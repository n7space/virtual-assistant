BLACK=black
PYTHON ?= python3

.PHONY : check \
	all \
	install \
	check-format \
	format

all: check-format check

install:
	${PYTHON} -m pip install --user --upgrade .

check:
	$(MAKE) -C tests check

check-format:
	${BLACK} --version
	${BLACK} --check vareq
	${BLACK} --check tests

format:
	${BLACK} vareq
	${BLACK} tests