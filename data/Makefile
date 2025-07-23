PYTHON ?= python3

.PHONY: all clean

ECSS_DOC=ECSS-E-ST-10-06C6March2009.pdf
REQUIREMENTS_TXT="ECSS-E-ST-10-06C-requirement-requirements.txt"
TYPES_TXT="ECSS-E-ST-10-06C-requirement-types.txt"

all: extract_requirements extract_types

${ECSS_DOC}:
	wget https://ecss.nl/wp-content/uploads/standards/ecss-e/ECSS-E-ST-10-06C6March2009.pdf

extract_requirements: ${ECSS_DOC}
	${PYTHON} extract.py --input ${ECSS_DOC} --output ${REQUIREMENTS_TXT} --preamble "Standard ECSS-E-ST-10-06C: Chapter " --start-page 24 --end-page 27
extract_types: ${ECSS_DOC}
	${PYTHON} extract.py --input ${ECSS_DOC} --output ${TYPES_TXT} --preamble "Standard ECSS-E-ST-10-06C: Chapter " --start-page 18 --end-page 21

clean:
	rm -f ${ECSS_DOC}
	rm -f ${REQUIREMENTS_TXT}
	rm -f ${TYPES_TXT}
