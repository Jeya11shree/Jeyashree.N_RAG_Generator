import pytest
from src import generate


def test_generate_answer_schema():
    out = generate.generate_answer("q", [])
    assert "answer" in out
    assert "evidence" in out
