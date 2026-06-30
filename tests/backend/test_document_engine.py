# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Test suite for Document Engine (Parser and Generator).
"""
import pytest
from pathlib import Path
from core.document.parser import parse_docx
from core.document.generator import generate_docx
from core.document.models import DocumentModel


# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def test_parse_simple_document():
    """Test parsing a simple Word document."""
    # This test requires a sample document
    sample_file = FIXTURES_DIR / "test_notice.docx"

    if not sample_file.exists():
        pytest.skip(f"Sample file not found: {sample_file}")

    # Parse the document
    model = parse_docx(sample_file)

    # Verify model structure
    assert isinstance(model, DocumentModel)
    assert len(model.paragraphs) > 0
    assert model.page_setup is not None
    assert model.metadata is not None

    print(f"Parsed {len(model.paragraphs)} paragraphs")
    print(f"Parsed {len(model.tables)} tables")


def test_generate_document():
    """Test generating a Word document from DocumentModel."""
    # Parse first
    sample_file = FIXTURES_DIR / "test_notice.docx"

    if not sample_file.exists():
        pytest.skip(f"Sample file not found: {sample_file}")

    model = parse_docx(sample_file)

    # Generate output
    output_file = FIXTURES_DIR / "test_output.docx"
    result_path = generate_docx(model, output_file)

    assert result_path.exists()
    assert result_path.stat().st_size > 0

    print(f"Generated document: {result_path}")


def test_roundtrip_consistency():
    """Test parse -> generate -> parse consistency."""
    sample_file = FIXTURES_DIR / "test_notice.docx"

    if not sample_file.exists():
        pytest.skip(f"Sample file not found: {sample_file}")

    # First parse
    model1 = parse_docx(sample_file)

    # Generate
    temp_file = FIXTURES_DIR / "temp_roundtrip.docx"
    generate_docx(model1, temp_file)

    # Second parse
    model2 = parse_docx(temp_file)

    # Compare
    assert len(model1.paragraphs) == len(model2.paragraphs)
    assert len(model1.tables) == len(model2.tables)

    # Compare text content
    for i, (p1, p2) in enumerate(zip(model1.paragraphs, model2.paragraphs)):
        assert p1.text == p2.text, f"Paragraph {i} text mismatch"

    print(f"Roundtrip test passed")

    # Cleanup
    if temp_file.exists():
        temp_file.unlink()


def test_model_serialization():
    """Test DocumentModel JSON serialization."""
    sample_file = FIXTURES_DIR / "test_notice.docx"

    if not sample_file.exists():
        pytest.skip(f"Sample file not found: {sample_file}")

    # Parse
    model = parse_docx(sample_file)

    # Serialize to JSON
    json_data = model.model_dump_json(indent=2)
    assert len(json_data) > 0

    # Deserialize
    model2 = DocumentModel.model_validate_json(json_data)
    assert len(model2.paragraphs) == len(model.paragraphs)

    print(f"Serialization test passed")


if __name__ == "__main__":
    # Run tests directly
    print("Testing Document Engine...")
    print()

    try:
        test_parse_simple_document()
        test_generate_document()
        test_roundtrip_consistency()
        test_model_serialization()
        print()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
