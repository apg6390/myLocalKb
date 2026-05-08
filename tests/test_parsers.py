from pathlib import Path

from backend.ingestion.parsers import parse_text


def test_parse_text_splits_on_blank_lines(tmp_path: Path) -> None:
    path = tmp_path / "notes.md"
    path.write_text("First paragraph\n\nSecond paragraph\n\n\nThird", encoding="utf-8")

    assert parse_text(path) == ["First paragraph", "Second paragraph", "Third"]
