"""
Snapshot tests for Document Parser and Generator.

These tests ensure the parser → generator pipeline produces consistent
output. Snapshots are stored as JSON files in tests/__snapshots__/.

Usage:
    pytest tests/backend/test_parser_snapshot.py -v --snapshot-update  (to update snapshots)
    pytest tests/backend/test_parser_snapshot.py -v                  (to verify)
"""
import json
import pytest
from pathlib import Path
from core.document.parser import parse_docx
from core.document.generator import generate_docx
from core.document.models import DocumentModel

# --- Paths ---
FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
SNAPSHOTS_DIR = Path(__file__).resolve().parent.parent / "__snapshots__"
SNAPSHOT_FILE = SNAPSHOTS_DIR / "test_notice_snapshot.json"
ROUNDTRIP_FILE = FIXTURES_DIR / "temp_roundtrip_snapshot.docx"

SAMPLE_FILE = FIXTURES_DIR / "test_notice.docx"


# === Helpers ===

def _normalize_model(model: DocumentModel) -> dict:
    """Serialize DocumentModel to a JSON-safe dict, excluding transient fields."""
    data = model.model_dump(mode="json", exclude={"filename", "source_path"})
    return data


def _load_snapshot() -> dict | None:
    """Load the stored snapshot, or None."""
    if not SNAPSHOT_FILE.exists():
        return None
    with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_snapshot(model: DocumentModel) -> None:
    """Persist the snapshot to disk."""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    data = _normalize_model(model)
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# === Tests ===

@pytest.mark.skipif(not SAMPLE_FILE.exists(), reason=f"Sample file not found: {SAMPLE_FILE}")
def test_parse_snapshot():
    """Test parsing produces consistent DocumentModel structure vs snapshot."""
    model = parse_docx(SAMPLE_FILE)
    current = _normalize_model(model)

    # Verify mode: compare against stored snapshot
    stored = _load_snapshot()
    if stored is None:
        _save_snapshot(model)
        pytest.skip("No snapshot found; created initial snapshot. Run again to verify.")

    # Compare key structural properties
    assert current["metadata"] == stored["metadata"], "Metadata mismatch"
    assert current["page_setup"] == stored["page_setup"], "PageSetup mismatch"
    assert len(current["paragraphs"]) == len(stored["paragraphs"]), "Paragraph count mismatch"
    assert len(current["tables"]) == len(stored["tables"]), "Table count mismatch"
    assert len(current["headers"]) == len(stored["headers"]), "Headers count mismatch"
    assert len(current["footers"]) == len(stored["footers"]), "Footers count mismatch"

    # Compare paragraph texts
    for i, (cp, sp) in enumerate(zip(current["paragraphs"], stored["paragraphs"])):
        assert cp["text"] == sp["text"], f"Paragraph {i} text mismatch"
        assert cp["role"] == sp["role"], f"Paragraph {i} role mismatch"

    # Compare table structure
    for i, (ct, st) in enumerate(zip(current["tables"], stored["tables"])):
        assert ct["rows"] == st["rows"], f"Table {i} row count mismatch"
        assert ct["cols"] == st["cols"], f"Table {i} col count mismatch"


@pytest.mark.skipif(not SAMPLE_FILE.exists(), reason=f"Sample file not found: {SAMPLE_FILE}")
def test_generate_roundtrip():
    """Test parse → generate → parse consistency."""
    # First parse
    model1 = parse_docx(SAMPLE_FILE)

    # Generate
    ROUNDTRIP_FILE.parent.mkdir(parents=True, exist_ok=True)
    result_path = generate_docx(model1, ROUNDTRIP_FILE)
    assert result_path.exists(), "Generated file does not exist"
    assert result_path.stat().st_size > 0, "Generated file is empty"

    # Second parse
    model2 = parse_docx(result_path)

    # Compare basic structure
    assert len(model1.paragraphs) == len(model2.paragraphs), \
        f"Paragraph count mismatch: {len(model1.paragraphs)} vs {len(model2.paragraphs)}"
    assert len(model1.tables) == len(model2.tables), \
        f"Table count mismatch: {len(model1.tables)} vs {len(model2.tables)}"

    # Compare text content of paragraphs
    for i, (p1, p2) in enumerate(zip(model1.paragraphs, model2.paragraphs)):
        assert p1.text == p2.text, f"Paragraph {i} text mismatch: {p1.text!r} vs {p2.text!r}"

    # Cleanup
    if ROUNDTRIP_FILE.exists():
        ROUNDTRIP_FILE.unlink()


@pytest.mark.skipif(not SAMPLE_FILE.exists(), reason=f"Sample file not found: {SAMPLE_FILE}")
def test_model_json_roundtrip():
    """Test DocumentModel JSON serialization → deserialization consistency."""
    model = parse_docx(SAMPLE_FILE)

    # Serialize to JSON
    json_data = model.model_dump_json(exclude={"filename", "source_path"})
    assert len(json_data) > 0, "Serialized JSON is empty"

    # Deserialize
    model2 = DocumentModel.model_validate_json(json_data)

    # Compare
    assert len(model2.paragraphs) == len(model.paragraphs), "Paragraph count mismatch after deserialization"
    assert len(model2.tables) == len(model.tables), "Table count mismatch after deserialization"
    for i, (p1, p2) in enumerate(zip(model.paragraphs, model2.paragraphs)):
        assert p1.text == p2.text, f"Paragraph {i} text mismatch after deserialization"
        assert p1.role == p2.role, f"Paragraph {i} role mismatch after deserialization"


@pytest.mark.skipif(not SAMPLE_FILE.exists(), reason=f"Sample file not found: {SAMPLE_FILE}")
def test_page_setup_preserved():
    """Test page setup properties survive the roundtrip."""
    model = parse_docx(SAMPLE_FILE)

    # Check page setup has values
    ps = model.page_setup
    assert ps is not None, "PageSetup should not be None"

    print(f"Page setup: width={ps.paper_width_mm}, height={ps.paper_height_mm}, "
          f"margin_top={ps.margin_top_mm}, margin_bottom={ps.margin_bottom_mm}, "
          f"margin_left={ps.margin_left_mm}, margin_right={ps.margin_right_mm}")

    # Roundtrip
    ROUNDTRIP_FILE.parent.mkdir(parents=True, exist_ok=True)
    generate_docx(model, ROUNDTRIP_FILE)
    model2 = parse_docx(ROUNDTRIP_FILE)

    # Compare page setup
    ps2 = model2.page_setup
    if ps.paper_width_mm and ps2.paper_width_mm:
        assert abs(ps.paper_width_mm - ps2.paper_width_mm) < 0.1, "Page width mismatch"
    if ps.margin_top_mm and ps2.margin_top_mm:
        assert abs(ps.margin_top_mm - ps2.margin_top_mm) < 0.1, "Margin top mismatch"

    # Cleanup
    if ROUNDTRIP_FILE.exists():
        ROUNDTRIP_FILE.unlink()


if __name__ == "__main__":
    print("Running snapshot tests...")
    test_parse_snapshot(snapshot_update=True)
    test_generate_roundtrip()
    test_model_json_roundtrip()
    test_page_setup_preserved()
    print("All tests passed!")
