#!/usr/bin/env bash
# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.
#
# gongwen-optimizer skill 安装器（macOS / Linux）
# 将 skill/ 源目录链接到各 Agent 平台的技能目录，源目录只维护一份。
#
# 用法:
#   bash skill/scripts/install.sh --all          # 安装到全部已知平台
#   bash skill/scripts/install.sh --list         # 列出目标目录
#   SKILL_DIRS="/path/a:/path/b" bash skill/scripts/install.sh   # 自定义目录
#
# 注意: 各平台技能目录路径随版本可能变化，请以本机实际为准。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SOURCE="$(cd "$SCRIPT_DIR/.." && pwd)"

# 已知平台技能目录（按需增删）
DEFAULT_TARGETS=(
  "$HOME/.claude/skills"            # Claude Code
  "$HOME/.codex/skills"             # Codex
  "$HOME/.config/opencode/skill"    # OpenCode
  "$HOME/.trae/skills"              # Trae Code
  "$HOME/.kimi/skills"              # Kimi Code
  "$HOME/.zcode/skills"             # ZCode
  "$HOME/.traework/skills"          # TraeWork
  "$HOME/.workbuddy/skills"         # WorkBuddy
  "$HOME/.cursor/skills"            # Cursor
)

TARGET_NAME="gongwen-optimizer"

resolve_targets() {
  if [[ -n "${SKILL_DIRS:-}" ]]; then
    IFS=':' read -ra _dirs <<< "$SKILL_DIRS"
    printf '%s\n' "${_dirs[@]}"
  else
    printf '%s\n' "${DEFAULT_TARGETS[@]}"
  fi
}

install_one() {
  local target="$1"
  local dest="$target/$TARGET_NAME"
  mkdir -p "$target"
  if [[ -e "$dest" || -L "$dest" ]]; then
    rm -rf "$dest"
  fi
  ln -s "$SKILL_SOURCE" "$dest"
  echo "[install] linked: $dest -> $SKILL_SOURCE"
}

case "${1:-}" in
  --list)
    echo "source: $SKILL_SOURCE"
    echo "targets:"
    resolve_targets | while read -r t; do echo "  $t/$TARGET_NAME"; done
    ;;
  --all|"")
    while read -r t; do
      [[ -z "$t" ]] && continue
      install_one "$t"
    done < <(resolve_targets)
    echo "[install] done. 若个别平台目录不存在，可稍后手动安装或设置 SKILL_DIRS 覆盖。"
    ;;
  *)
    echo "usage: $0 [--all|--list]" >&2
    exit 1
    ;;
esac
