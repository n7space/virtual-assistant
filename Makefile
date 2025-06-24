BLACK=black
PYTHON ?= python3

.PHONY : check \
	all \
	install \
	check-format \
	format

all: check-format check

install: install-pipx

# Perform a native installation
install-native:
	${PYTHON} -m pip install --user --upgrade .

# Perform pipx installation (in a transparent venv)
install-pipx:
	pipx install .

# Create a virtual environment and perform an isolated installation
install-venv:
	${PYTHON} -m venv venv
	. venv/bin/activate && ${PYTHON} -m pip install --upgrade pip
	. venv/bin/activate && ${PYTHON} -m pip install .

clean-venv:
	rm -rf venv

check:
	$(MAKE) -C tests check

check-format:
	${BLACK} --version
	${BLACK} --check vareq
	${BLACK} --check tests
	${BLACK} --check data

format:
	${BLACK} vareq
	${BLACK} tests
	${BLACK} data