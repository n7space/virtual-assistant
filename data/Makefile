PYTHON ?= python3

all: extract_requirements extract_types

extract_requirements:
	${PYTHON} extract.py --input "ECSS-E-ST-10-06C(6March2009).pdf" --output "ECSS-E-ST-10-06C - requirement requirements.txt" --preamble "Standard ECSS-E-ST-10-06C: Chapter " --start-page 24 --end-page 27
extract_types:
	${PYTHON} extract.py --input "ECSS-E-ST-10-06C(6March2009).pdf" --output "ECSS-E-ST-10-06C - requirement types.txt" --preamble "Standard ECSS-E-ST-10-06C: Chapter " --start-page 18 --end-page 21