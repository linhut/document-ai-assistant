# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Test suite for Rule Engine (Checker and Fixer).
"""
import pytest
from pathlib import Path

from core.document.parser import parse_docx
from core.document.generator import generate_docx
from core.rules.engine import RuleEngine
from core.rules.checker import CheckIssue


# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def test_rule_engine_check():
    """Test rule engine checking functionality."""
    sample_file = FIXTURES_DIR / "test_notice.docx"

    if not sample_file.exists():
        pytest.skip(f"Sample file not found: {sample_file}")

    # Parse document
    model = parse_docx(sample_file)

    # Run checks
    engine = RuleEngine()
    issues = engine.check(model, doc_type="notice")

    # Verify issues found
    assert isinstance(issues, list)
    print(f"Found {len(issues)} issues:")
    for issue in issues[:5]:  # Print first 5
        print(f"  - [{issue.severity}] {issue.name}: {issue.reason}")

    # Should find some issues (test doc is not perfectly formatted)
    assert len(issues) > 0


def test_rule_engine_fix():
    """Test rule engine fixing functionality."""
    sample_file = FIXTURES_DIR / "test_notice.docx"

    if not sample_file.exists():
        pytest.skip(f"Sample file not found: {sample_file}")

    # Parse document
    model = parse_docx(sample_file)

    # Apply fixes
    engine = RuleEngine()
    fixed_model = engine.fix(model, doc_type="notice")

    # Verify model was modified
    assert fixed_model is not None
    assert len(fixed_model.paragraphs) > 0

    # Generate fixed document
    output_file = FIXTURES_DIR / "test_notice_fixed.docx"
    generate_docx(fixed_model, output_file)

    assert output_file.exists()
    print(f"Generated fixed document: {output_file}")


def test_rule_engine_check_and_fix():
    """Test combined check and fix."""
    sample_file = FIXTURES_DIR / "test_notice.docx"

    if not sample_file.exists():
        pytest.skip(f"Sample file not found: {sample_file}")

    # Parse document
    model = parse_docx(sample_file)

    # Check and fix
    engine = RuleEngine()
    issues, fixed_model = engine.check_and_fix(model, doc_type="notice")

    # Verify results
    assert len(issues) > 0
    assert fixed_model is not None

    # Check if fixes reduced issues
    issues_after = engine.check(fixed_model, doc_type="notice")

    p0_before = sum(1 for i in issues if i.severity == "P0")
    p0_after = sum(1 for i in issues_after if i.severity == "P0")

    print(f"Issues before fix: {len(issues)} (P0={p0_before})")
    print(f"Issues after fix: {len(issues_after)} (P0={p0_after})")

    # After fixing, P0 issues should decrease (format errors fixed)
    # P1 issues may fluctuate due to fix rule side effects (e.g., body align vs signature align)
    assert p0_after <= p0_before, f"P0 issues increased: {p0_before} -> {p0_after}"


def test_available_document_types():
    """Test listing available document types."""
    engine = RuleEngine()
    types = engine.available_types()

    assert isinstance(types, list)
    assert len(types) > 0
    assert "notice" in types

    print(f"Available document types: {types}")


if __name__ == "__main__":
    print("Testing Rule Engine...")
    print()

    try:
        test_rule_engine_check()
        test_rule_engine_fix()
        test_rule_engine_check_and_fix()
        test_available_document_types()
        print()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
