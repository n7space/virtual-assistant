from vareq import vaknowledgelibrary
import logging
import pytest
import os

TEST_DIR: str = os.path.dirname(os.path.realpath(__file__))
RESOURCE_DIR: str = os.path.join(TEST_DIR, "resources")
logging.basicConfig(level=logging.DEBUG)

def test_docx_is_read_properly():
    library = vaknowledgelibrary.KnowledgeLibrary()
    path = os.path.join(RESOURCE_DIR, "test docx.docx")

    text = library.read_document(path)

    assert text is not None
    assert 10 < len(text)
    assert "Static Architecture" in text