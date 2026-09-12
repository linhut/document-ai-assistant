# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""gongwen-optimizer skill 打包测试（原创实现）。"""

import tempfile
import zipfile
from pathlib import Path

from scripts.build_skill_zip import SKILL_DIR, build_zip

# 让 scripts 包可导入（tests 根目录已在 sys.path）
import sys  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_skill_md_exists_and_mentions_engine():
    skill_md = SKILL_DIR / "SKILL.md"
    assert skill_md.exists()
    content = skill_md.read_text(encoding="utf-8")
    assert "GB/T 9704" in content
    assert "wfp_cli" in content
    assert "format" in content and "check" in content


def test_install_scripts_present():
    sh = SKILL_DIR / "scripts" / "install.sh"
    ps1 = SKILL_DIR / "scripts" / "install.ps1"
    assert sh.exists() and sh.stat().st_size > 500
    assert ps1.exists() and ps1.stat().st_size > 500
    sh_text = sh.read_text(encoding="utf-8")
    assert ".claude/skills" in sh_text and "SKILL_DIRS" in sh_text
    ps1_text = ps1.read_text(encoding="utf-8")
    assert ".claude\\skills" in ps1_text or ".claude/skills" in ps1_text
    assert "SKILL_DIRS" in ps1_text


def test_build_zip_contains_skill_md():
    with tempfile.TemporaryDirectory() as tmp:
        out = build_zip(Path(tmp) / "gongwen-skill.zip")
        with zipfile.ZipFile(out) as zf:
            names = zf.namelist()
        assert "SKILL.md" in names
        assert any(n.endswith("install.sh") for n in names)
        assert any(n.endswith("install.ps1") for n in names)