import pytest
import logging
from vareq.helpers import (
    cosine_similarity,
    remove_think_markers,
    extract_number
)

logging.basicConfig(level=logging.DEBUG)


def test_cosine_similarity_identical():
    v1 = [1.0, 2.0, 3.0]
    v2 = [1.0, 2.0, 3.0]
    assert pytest.approx(cosine_similarity(v1, v2), 0.0001) == 1.0


def test_cosine_similarity_orthogonal():
    v1 = [1, 0]
    v2 = [0, 1]
    assert pytest.approx(cosine_similarity(v1, v2), 0.0001) == 0.0


def test_cosine_similarity_zero_vector():
    v1 = [0, 0, 0]
    v2 = [1, 2, 3]
    assert cosine_similarity(v1, v2) == 0.0


def test_remove_think_markers_basic():
    text = "This is <think>hidden</think> visible."
    assert remove_think_markers(text) == "This is  visible."


def test_remove_think_markers_none():
    assert remove_think_markers(None) is None


def test_remove_think_markers_multiple():
    text = "A<think>1</think>B<think>2</think>C"
    assert remove_think_markers(text) == "ABC"


def test_extract_number_float():
    assert extract_number("The value is 3.14.") == 3.14


def test_extract_number_int():
    assert extract_number("The answer is 42, always") == 42.0


def test_extract_number_none():
    assert extract_number(None) == 0.0


def test_extract_number_no_number():
    assert extract_number("Lorem possum") == 0.0
