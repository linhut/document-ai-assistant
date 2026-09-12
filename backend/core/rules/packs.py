# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
标准包机制（原创实现）。

标准包 = 一套可替换官方规则的规则目录（rules/packs/<包名>/），
用于按单位/行业采用不同的公文格式基准（如企业公文、党政机关、军队公文等）。

优先级：official < pack < custom < user。

当前激活的包持久化在 APP_DATA_DIR/active_pack.json；
不激活时（None）完全使用官方规则，行为与旧版本一致。
"""

from __future__ import annotations

import json
from pathlib import Path

from config import APP_DATA_DIR, RULES_DIR
from utils.logger import logger

PACKS_DIR = RULES_DIR.parent / "packs"
ACTIVE_PACK_FILE = APP_DATA_DIR / "active_pack.json"


def list_standard_packs() -> list[str]:
    """返回可用标准包名（目录下至少含一个 .yaml 规则文件）。"""
    if not PACKS_DIR.exists():
        return []
    packs = []
    for d in sorted(PACKS_DIR.iterdir()):
        if d.is_dir() and any(d.glob("*.yaml")):
            packs.append(d.name)
    return packs


def _load_active_file() -> str | None:
    if not ACTIVE_PACK_FILE.exists():
        return None
    try:
        data = json.loads(ACTIVE_PACK_FILE.read_text(encoding="utf-8"))
        return str(data.get("pack") or "") or None
    except Exception:
        return None


def get_active_pack() -> str | None:
    """返回当前激活的标准包名；未激活返回 None。"""
    name = _load_active_file()
    if name and name in list_standard_packs():
        return name
    return None


def set_active_pack(name: str | None) -> bool:
    """
    激活（或停用）标准包。

    Args:
        name: 标准包名；None 或空串表示停用（恢复官方规则）。

    Returns:
        是否设置成功（包不存在时返回 False）。
    """
    if name:
        if name not in list_standard_packs():
            logger.error(f"标准包不存在: {name}")
            return False
        ACTIVE_PACK_FILE.parent.mkdir(parents=True, exist_ok=True)
        ACTIVE_PACK_FILE.write_text(
            json.dumps({"pack": name}, ensure_ascii=False), encoding="utf-8"
        )
        logger.info(f"Standard pack activated: {name}")
    else:
        if ACTIVE_PACK_FILE.exists():
            ACTIVE_PACK_FILE.unlink()
        logger.info("Standard pack deactivated (official rules)")
    return True


def resolve_pack_dirs(pack: str | None = None) -> list[tuple[str, Path]]:
    """
    返回规则层目录列表（含可选的标准包层）。

    返回 [(source_label, dir_path), ...]，顺序即优先级（后者覆盖前者）。
    """
    from core.rules.manager import OFFICIAL_RULES_DIR, CUSTOM_RULES_DIR, USER_RULES_DIR

    layers: list[tuple[str, Path]] = [("official", OFFICIAL_RULES_DIR)]
    active = pack or get_active_pack()
    if active:
        pack_dir = PACKS_DIR / active
        if pack_dir.is_dir():
            layers.append((f"pack:{active}", pack_dir))
    layers.extend(
        [
            ("custom", CUSTOM_RULES_DIR),
            ("user", USER_RULES_DIR),
        ]
    )
    return layers