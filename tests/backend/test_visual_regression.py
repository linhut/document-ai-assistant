# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""视觉回归库单元测试（原创实现；渲染环节缺失时自动跳过）。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "visual_regression"))

import pytest  # noqa: E402
from PIL import Image  # noqa: E402

from vr_lib import (  # noqa: E402
    GOLDEN_TYPES,
    build_baseline,
    compare_baselines,
    generate_golden,
    golden_model,
    hash_distance,
    image_average_hash,
)

DIMS = (64, 64)


def _solid(color):
    return Image.new("L", DIMS, color)


def _with_square(pos):
    """在白色画布 (pos) 处画一个黑色方块，构造有结构的图像。"""
    from PIL import ImageDraw

    img = Image.new("L", DIMS, 255)
    draw = ImageDraw.Draw(img)
    x, y = pos
    draw.rectangle([x, y, x + 20, y + 20], fill=0)
    return img


def test_identical_images_zero_distance():
    a = image_average_hash(_solid(120))
    b = image_average_hash(_solid(120))
    assert hash_distance(a, b) == 0


def test_different_images_positive_distance():
    # 纯色图对 aHash 是病态输入（均值饱和），用有结构的内容断言差异
    a = image_average_hash(_with_square((8, 8)))
    b = image_average_hash(_with_square((36, 8)))
    assert hash_distance(a, b) > 0


def test_golden_model_has_expected_roles():
    model = golden_model("notice")
    roles = [p.role for p in model.paragraphs]
    assert "title" in roles and "body" in roles and "signature" in roles and "date" in roles


def test_generate_golden_produces_docx(tmp_path):
    for doc_type in GOLDEN_TYPES:
        out = generate_golden(doc_type, tmp_path / doc_type / f"{doc_type}.docx")
        assert out.exists() and out.stat().st_size > 500


def test_build_baseline_without_render(tmp_path):
    docx = generate_golden("notice", tmp_path / "notice.docx")
    baseline = build_baseline(docx, tmp_path / "render")
    assert "docx_sha256" in baseline
    assert baseline["docx_sha256"]  # 非空


def test_compare_baselines_identical_docx_passes():
    left = {"docx_sha256": "abc", "pages": [], "renderable": False}
    right = {"docx_sha256": "abc", "pages": [], "renderable": False}
    assert compare_baselines(left, right)["pass"]


def test_compare_baselines_different_docx_fails():
    left = {"docx_sha256": "abc", "pages": [], "renderable": False}
    right = {"docx_sha256": "xyz", "pages": [], "renderable": False}
    assert not compare_baselines(left, right)["pass"]