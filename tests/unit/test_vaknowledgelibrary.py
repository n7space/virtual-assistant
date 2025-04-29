from vareq import vaknowledgelibrary
from vareq import vallminterface
from vareq import varequirementreader
from typing import List
import tempfile
import logging
import pytest
import os

TEST_DIR: str = os.path.dirname(os.path.realpath(__file__))
RESOURCE_DIR: str = os.path.join(TEST_DIR, "resources")
logging.basicConfig(level=logging.DEBUG)


class FakeLlm(vallminterface.Llm):
    def embedding(self, text: str) -> List[float]:
        # Differentiate by length to support fake relevance searches
        result = [len(text), 2, 3, 4]
        return result


def test_docx_is_read_properly():
    llm = None  # unused
    config = vaknowledgelibrary.KnowledgeLibraryConfig()  # default
    library = vaknowledgelibrary.KnowledgeLibrary(llm, config)
    path = os.path.join(RESOURCE_DIR, "test docx.docx")

    text = library.read_document(path)

    assert text is not None
    assert 10 < len(text)
    assert " Static Architecture of the Universal Army Potato" in text


def test_pdf_is_read_properly():
    llm = None  # unused
    config = vaknowledgelibrary.KnowledgeLibraryConfig()  # default
    library = vaknowledgelibrary.KnowledgeLibrary(llm, config)
    path = os.path.join(RESOURCE_DIR, "test pdf.pdf")

    text = library.read_document(path)

    assert text is not None
    assert 10 < len(text)
    assert " Static Architecture of the Universal Army Potato" in text


def test_txt_is_read_properly():
    llm = None  # unused
    config = vaknowledgelibrary.KnowledgeLibraryConfig()  # default
    library = vaknowledgelibrary.KnowledgeLibrary(llm, config)
    path = os.path.join(RESOURCE_DIR, "test txt.txt")

    text = library.read_document(path)

    assert text is not None
    assert 10 < len(text)
    assert " Static Architecture of the Universal Army Potato" in text


def test_text_is_split_properly():
    llm = None  # unused
    config = vaknowledgelibrary.KnowledgeLibraryConfig()  # default
    config.chunk_size = 1000
    config.chunk_overlap = 100
    library = vaknowledgelibrary.KnowledgeLibrary(llm, config)
    path = os.path.join(RESOURCE_DIR, "long text.txt")
    text = library.read_document(path)

    chunks = library.split_text(text)

    assert chunks is not None
    assert 36 == len(chunks)
    assert 922 == len(chunks[0])


def test_registering_document_works():
    db_path = os.path.join(tempfile.mkdtemp(), "db")
    llm = FakeLlm()
    config = vaknowledgelibrary.KnowledgeLibraryConfig()  # default
    config.persistent_storage_path = db_path
    library = vaknowledgelibrary.KnowledgeLibrary(llm, config)

    library.register_document("Test1", "test1.txt", 200, "Lorem Ipsum")
    library.register_document("Test2", "test2.txt", 500, "Lorem Ipsum")

    timestamp1 = library.get_document_timestamp("test1.txt")
    timestamp2 = library.get_document_timestamp("test2.txt")
    assert 200 == timestamp1
    assert 500 == timestamp2


def test_searching_for_relevant_documents_work():
    db_path = os.path.join(tempfile.mkdtemp(), "db")
    llm = FakeLlm()
    config = vaknowledgelibrary.KnowledgeLibraryConfig()  # default
    config.persistent_storage_path = db_path
    library = vaknowledgelibrary.KnowledgeLibrary(llm, config)
    library.register_document("Test1", "test1.txt", 200, "Car")
    library.register_document("Test2", "test2.txt", 500, "Elephant")
    library.register_document("Test3", "test3.txt", 500, "Moto")

    docs = library.get_relevant_documents("Car", 2)

    assert 2 == len(docs)
    assert "### Document Test1 part 0\nCar" == docs[0]
    assert "### Document Test3 part 0\nMoto" == docs[1]


def test_adding_document_works():
    file1 = tempfile.NamedTemporaryFile(mode="w+t", delete=False)
    file1.write("Cats are awesome")
    file1.close()
    db_path = os.path.join(tempfile.mkdtemp(), "db")
    llm = FakeLlm()
    config = vaknowledgelibrary.KnowledgeLibraryConfig()  # default
    config.persistent_storage_path = db_path
    library = vaknowledgelibrary.KnowledgeLibrary(llm, config)

    added = library.add_document(file1.name)

    docs = library.get_relevant_documents("Cats", 1)
    assert 1 == len(docs)
    assert "awesome" in docs[0]
    assert added


def test_adding_directory_works():
    db_path = os.path.join(tempfile.mkdtemp(), "db")
    llm = FakeLlm()
    config = vaknowledgelibrary.KnowledgeLibraryConfig()  # default
    config.persistent_storage_path = db_path
    library = vaknowledgelibrary.KnowledgeLibrary(llm, config)

    # reuse resources dir
    library.add_directory(RESOURCE_DIR)

    docs = library.get_all_documents()
    headers = [doc.splitlines()[0] for doc in docs]
    assert 3 <= len(docs)
    assert "### Document test txt part 0" in headers


def test_deleting_documents_works():
    db_path = os.path.join(tempfile.mkdtemp(), "db")
    llm = FakeLlm()
    config = vaknowledgelibrary.KnowledgeLibraryConfig()  # default
    config.persistent_storage_path = db_path
    library = vaknowledgelibrary.KnowledgeLibrary(llm, config)
    library.register_document("Test1", "test1.txt", 200, "Car")
    library.register_document("Test2", "test2.txt", 500, "Elephant")
    library.register_document("Test3", "test3.txt", 500, "Moto")

    library.delete_all_documents()

    docs = library.get_relevant_documents("Car", 2)
    assert 0 == len(docs)


def test_adding_requirements_works():
    db_path = os.path.join(tempfile.mkdtemp(), "db")
    llm = FakeLlm()
    config = vaknowledgelibrary.KnowledgeLibraryConfig()  # default
    config.persistent_storage_path = db_path
    library = vaknowledgelibrary.KnowledgeLibrary(llm, config)
    req1 = varequirementreader.Requirement("REQ-FUN-12", "It should work")
    req2 = varequirementreader.Requirement("REQ-FUN-30", "It should dance")

    library.add_requirements([req1, req2])

    docs = library.get_relevant_documents("working", 2)
    assert 2 == len(docs)
    assert "REQ-FUN-12" in docs[0] or "REQ-FUN-12" in docs[1]
    assert "REQ-FUN-30" in docs[0] or "REQ-FUN-30" in docs[1]


def test_deleting_requirements_works():
    db_path = os.path.join(tempfile.mkdtemp(), "db")
    llm = FakeLlm()
    config = vaknowledgelibrary.KnowledgeLibraryConfig()  # default
    config.persistent_storage_path = db_path
    library = vaknowledgelibrary.KnowledgeLibrary(llm, config)
    req1 = varequirementreader.Requirement("REQ-FUN-12", "It should work")
    req2 = varequirementreader.Requirement("REQ-FUN-30", "It should dance")
    library.add_requirements([req1, req2])

    library.delete_all_requirements()

    docs = library.get_relevant_documents("working", 2)
    assert 0 == len(docs)
