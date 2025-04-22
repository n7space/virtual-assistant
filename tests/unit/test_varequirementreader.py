from vareq import varequirementreader
import logging
import pytest
import os

TEST_DIR: str = os.path.dirname(os.path.realpath(__file__))
RESOURCE_DIR: str = os.path.join(TEST_DIR, "resources")
logging.basicConfig(level=logging.DEBUG)


def test_mappings_init():
    mappings = varequirementreader.Mappings()

    # Column mappings based on MBEP-KISPE-EP-SRS-001 v1.0
    # Test only the most critical ones
    assert "5. Requirements" == mappings.worksheet_name
    assert 3 == mappings.first_row_number
    assert "A" == mappings.id
    assert "C" == mappings.description
    assert "G" == mappings.note
    assert "E" == mappings.justification


def test_mappings_update_from_dict():
    dictionary = {
        "id": "X",
        "description": "Y",
        "note": "Z",
        "justification": "AA",
        "first_row_number": 100,
        "worksheet_name": "reqs",
    }

    mappings = varequirementreader.Mappings().update_from_dict(dictionary)

    assert "reqs" == mappings.worksheet_name
    assert 100 == mappings.first_row_number
    assert "X" == mappings.id
    assert "Y" == mappings.description
    assert "Z" == mappings.note
    assert "AA" == mappings.justification


def test_requirements_are_read():
    path = os.path.join(RESOURCE_DIR, "test_requirements.xlsx")
    mappings = varequirementreader.Mappings().update_from_dict(
        {"worksheet_name": "reqs"}
    )
    reader = varequirementreader.VaRequirementReader(mappings)

    requirements = reader.read_requirements(path)

    # Check the number of requirements read
    assert 10 == len(requirements)
    # Check representative requirements
    # Basic data and justification
    req10 = requirements[0]
    assert "REQ-10" == req10.id
    assert "functional" == req10.type
    assert "ASW shall do things" == req10.description
    assert "Because" == req10.justification
    assert "T" == req10.validation_type
    assert 1 == len(req10.traces)
    assert "BR-10" == req10.traces[0]
    assert req10.note is None
    # Empty traces
    req20 = requirements[1]
    assert "REQ-20" == req20.id
    assert 0 == len(req20.traces)
    # More than one trace
    req30 = requirements[2]
    assert "REQ-30" == req30.id
    assert 2 == len(req30.traces)
    assert "BR-40" == req30.traces[0]
    assert "BR-60" == req30.traces[1]
    # Different validation method
    req50 = requirements[4]
    assert "REQ-50" == req50.id
    assert "D" == req50.validation_type
    # Note
    req90 = requirements[8]
    assert "REQ-90" == req90.id
    assert "Like a panda" == req90.note
