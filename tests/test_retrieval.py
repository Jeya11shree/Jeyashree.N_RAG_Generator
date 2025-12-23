import pytest
from src import retrieval


def test_retrieve_returns_list():
    out = retrieval.retrieve("query")
    assert isinstance(out, list)
