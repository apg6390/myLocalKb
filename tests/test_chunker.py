import pytest

from backend.ingestion.chunker import chunk_text


def test_chunk_text_uses_sliding_window_with_overlap() -> None:
    chunks = chunk_text(["abcdefghij"], chunk_size=4, overlap=1)

    assert [chunk["text"] for chunk in chunks] == ["abcd", "defg", "ghij"]
    assert [chunk["page"] for chunk in chunks] == [1, 1, 1]
    assert [chunk["chunk_index"] for chunk in chunks] == [0, 1, 2]


def test_chunk_text_skips_empty_pages() -> None:
    chunks = chunk_text(["", "  useful text  "], chunk_size=20, overlap=2)

    assert chunks == [{"text": "useful text", "page": 2, "chunk_index": 0}]


def test_chunk_text_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        chunk_text(["text"], chunk_size=4, overlap=4)
