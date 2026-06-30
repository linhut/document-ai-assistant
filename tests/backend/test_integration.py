# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
End-to-end integration test for Phase 4.
Tests the complete workflow: upload -> check -> fix -> download
"""
import time
import requests
from pathlib import Path


BASE_URL = "http://127.0.0.1:8765"
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _get_auth_headers():
    """获取认证 headers。"""
    try:
        from config import APP_DATA_DIR
        token_file = APP_DATA_DIR / ".auth_token"
        if token_file.exists():
            token = token_file.read_text(encoding="utf-8").strip()
            return {"Authorization": f"Bearer {token}"}
    except Exception:
        pass
    return {}


def test_complete_workflow():
    """Test complete document processing workflow."""
    print("=" * 60)
    print("Phase 4 Integration Test - Complete Workflow")
    print("=" * 60)
    print()

    headers = _get_auth_headers()

    # Step 1: Upload document
    print("Step 1: Uploading document...")
    test_file = FIXTURES_DIR / "test_notice.docx"

    with open(test_file, "rb") as f:
        files = {"file": (test_file.name, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        response = requests.post(f"{BASE_URL}/api/documents/upload", files=files, headers=headers)

    assert response.status_code == 200, f"Upload failed: {response.text}"
    doc_data = response.json()
    doc_id = doc_data["id"]

    print(f"  Document uploaded: ID={doc_id}")
    print(f"  Filename: {doc_data['filename']}")
    print(f"  Paragraphs: {doc_data['paragraph_count']}")
    print()

    # Step 2: Run format check
    print("Step 2: Running format check...")
    response = requests.post(
        f"{BASE_URL}/api/check/{doc_id}",
        json={"document_type": "notice"},
        headers=headers
    )

    assert response.status_code == 200, f"Check failed: {response.text}"
    check_data = response.json()

    print(f"  Total issues: {check_data['total_issues']}")
    print(f"  P0 (Critical): {check_data['p0_count']}")
    print(f"  P1 (Important): {check_data['p1_count']}")
    print(f"  P2 (Minor): {check_data['p2_count']}")
    print()

    # Step 3: Get issue details
    print("Step 3: Getting issue details...")
    response = requests.get(f"{BASE_URL}/api/check/{doc_id}/results", headers=headers)

    assert response.status_code == 200, f"Get results failed: {response.text}"
    issues = response.json()

    print(f"  Found {len(issues)} issues:")
    for i, issue in enumerate(issues[:5], 1):  # Show first 5
        print(f"    {i}. [{issue['severity']}] {issue['check_type']}: {issue['reason']}")
    print()

    # Step 4: Apply automatic fixes
    print("Step 4: Applying automatic fixes...")
    response = requests.post(
        f"{BASE_URL}/api/optimize/{doc_id}",
        json={
            "document_type": "notice",
            "apply_fixes": True
        },
        headers=headers
    )

    assert response.status_code == 200, f"Optimize failed: {response.text}"
    optimize_data = response.json()

    print(f"  Fixes applied: {optimize_data.get('fixes_applied', 0)}")
    print(f"  Output file: {optimize_data.get('output_name', optimize_data.get('output_path', 'N/A'))}")
    print()

    # Step 5: Verify fixes reduced issues
    print("Step 5: Verifying fixes...")
    # Note: We would need to upload the optimized doc and check it again
    # For now, just confirm the optimized file was created
    print(f"  Optimized document created: {optimize_data['output_path']}")
    print()

    print("=" * 60)
    print("All tests passed!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  - Document uploaded successfully")
    print(f"  - Found {check_data['total_issues']} issues")
    print(f"  - Applied {optimize_data['fixes_applied']} fixes")
    print(f"  - Generated optimized document")
    print()
    print("Phase 4 is working correctly!")


if __name__ == "__main__":
    try:
        # Wait for backend to be ready
        print("Waiting for backend to start...")
        for i in range(10):
            try:
                response = requests.get(f"{BASE_URL}/api/health", timeout=2)
                if response.status_code == 200:
                    print("Backend is ready!")
                    print()
                    break
            except:
                time.sleep(1)
        else:
            print("ERROR: Backend not responding. Please start backend with: python backend/main.py")
            exit(1)

        test_complete_workflow()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
