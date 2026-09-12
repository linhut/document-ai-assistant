# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""暗标合规检查模块单元测试（原创实现）。"""

from core.compliance.dark_bid import (
    DARK_BID_RULES,
    dark_bid_check,
    id_check_digit,
)
from core.document.models import DocumentModel, Paragraph, Table, TableCell


def _model(texts: list[str]) -> DocumentModel:
    return DocumentModel(
        paragraphs=[Paragraph(index=i, text=t) for i, t in enumerate(texts)]
    )


def _ids(issues) -> set[str]:
    return {i.rule_id for i in issues}


def test_id_check_digit_algorithm():
    # 构造合法的 18 位身份证：前 17 位 + 校验位
    base = "110105199003075" + "1" * 3  # 前 17 位
    check = id_check_digit(base)
    assert check in "0123456789X"


def test_valid_idcard_detected_and_masked():
    base17 = "11010519900307511"
    id18 = base17 + id_check_digit(base17)
    model = _model([f"联系人：{id18}"])
    issues = dark_bid_check(model)
    assert "DKB-C001" in _ids(issues)
    # 输出必须脱敏：不含完整身份证
    assert id18 not in issues[0].original_text
    assert issues[0].original_text.count("*") >= 8


def test_mobile_detected():
    model = _model(["联系电话：13812345678"])
    assert "DKB-C002" in _ids(dark_bid_check(model))


def test_email_detected():
    model = _model(["联系邮箱：zhangsan@example.com"])
    assert "DKB-C003" in _ids(dark_bid_check(model))


def test_bank_card_detected():
    model = _model(["收款账号：6222021234567890123"])
    assert "DKB-C004" in _ids(dark_bid_check(model))


def test_long_numbers_not_misreported():
    # 普通长数字（如日期+编号拼接）不应误报身份证
    model = _model(["编号：2026091100001234"])
    assert "DKB-C001" not in _ids(dark_bid_check(model))


def test_table_cells_scanned():
    model = DocumentModel(
        paragraphs=[],
        tables=[
            Table(
                index=0,
                rows=1,
                cols=1,
                cells=[
                    TableCell(
                        row=0,
                        col=0,
                        text="联系人手机 13900000001",
                        paragraphs=[Paragraph(index=0, text="联系人手机 13900000001")],
                    )
                ],
            )
        ],
    )
    assert "DKB-C002" in _ids(dark_bid_check(model))


def test_clean_document_no_issues():
    model = _model(["本方案报价 128000 元，工期 90 天。", "特此说明。"])
    assert dark_bid_check(model) == []


def test_registry_complete():
    assert {r["id"] for r in DARK_BID_RULES} == {"DKB-C001", "DKB-C002", "DKB-C003", "DKB-C004"}