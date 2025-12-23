import pytest
from src import ingest


def test_parse_file_returns_dict():
    out = ingest.parse_file("sample")
    assert isinstance(out, dict)
