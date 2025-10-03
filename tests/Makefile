SRC_DIR = ../

.PHONY : \
	check \
	integration \
	unit

unit:
	${MAKE} -C $@ check

integration:
	${MAKE} -C $@ check

check: unit integration