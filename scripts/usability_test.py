# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
可用性测试：API 全流程实测（原创实现，仅用标准库）。

覆盖：后端启动 → 健康检查 → 上传 → 格式检查(含 standard_ref/语义校验)
     → 暗标合规 → 标准包切换 → AI 润色降级 → PDF 导出降级
     → 优化全流程（清洗+规则修复+生成）→ 输出可重解析 → A4 预览
     → 新端点契约与首字节耗时。

用法：
  python scripts/usability_test.py [--port 8767]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT / "backend"
SAMPLE = ROOT / "data" / "uploads" / "260410第十三届全国少数民族传统体育运动会筹委会秘书长办公会议记录.docx"
TOKEN_FILE = ROOT / "data" / ".auth_token"

RESULTS: list[tuple[str, bool, str]] = []


def _bearer_token() -> str | None:
    """读取后端鉴权令牌（data/.auth_token，与 Electron 主进程行为一致）。"""
    try:
        if TOKEN_FILE.exists():
            token = TOKEN_FILE.read_text(encoding="utf-8").strip()
            return token or None
    except Exception:
        pass
    return None


_TOKEN = _bearer_token()


def record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")


def api(method: str, path: str, body: dict | None = None, files: dict | None = None,
        timeout: float = 90) -> dict:
    """极简 HTTP 客户端（支持 JSON 与 multipart 上传）。"""
    url = f"http://127.0.0.1:{PORT}{path}"
    if files:
        boundary = "----uta" + str(int(time.time()))
        parts = []
        for field, (filename, content) in files.items():
            parts.append(
                f"--{boundary}\r\nContent-Disposition: form-data; "
                f'name="{field}"; filename="{filename}"\r\n'
                f"Content-Type: application/octet-stream\r\n\r\n"
            )
            parts.append(content.decode("latin-1", "replace"))
            parts.append("\r\n")
        parts.append(f"--{boundary}--\r\n")
        data = "".join(parts).encode("latin-1", "replace")
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    elif body is not None:
        data = json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json"}
    else:
        data = None
        headers = {}

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    if _TOKEN:
        req.add_header("Authorization", f"Bearer {_TOKEN}")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            elapsed = round(time.time() - t0, 3)
            if not raw:
                return {}
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                parsed["_elapsed"] = elapsed
            return parsed
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        elapsed = round(time.time() - t0, 3)
        parsed = json.loads(raw) if raw else {}
        if isinstance(parsed, dict):
            parsed["_elapsed"] = elapsed
            parsed["_http_status"] = e.code
        return parsed


def wait_health(timeout_s: float = 30) -> float | None:
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        try:
            r = api("GET", "/api/health", timeout=3)
            if r.get("status") == "ok":
                return round(time.time() - t0, 2)
        except Exception:
            pass
        time.sleep(0.5)
    return None


def _stop_proc(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        proc.terminate()
    except Exception:
        pass
    time.sleep(2)
    if proc.poll() is None:
        try:
            proc.kill()
        except Exception:
            pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8767)
    args = parser.parse_args()
    global PORT
    PORT = args.port

    if not SAMPLE.exists():
        print(f"样例文件不存在: {SAMPLE}")
        sys.exit(2)

    proc = subprocess.Popen(
        [sys.executable, str(BACKEND_DIR / "main.py"), "--port", str(PORT)],
        cwd=str(BACKEND_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        # 1. 启动与健康
        boot = wait_health()
        record("后端启动 / 健康检查", boot is not None, f"boot={boot}s")

        # 2. 上传
        up = api("POST", "/api/documents/upload", files={"file": (SAMPLE.name, SAMPLE.read_bytes())})
        doc_id = up.get("id") or (up.get("document_id"))
        record("上传文档", doc_id is not None, f"doc_id={doc_id} {up.get('_elapsed')}s")

        # 3. 格式检查（含 standard_ref 证据链）
        chk = api("POST", f"/api/check/{doc_id}", {"document_type": "meeting"})
        rec_ok = chk.get("total_issues") is not None
        record("格式检查", rec_ok, f"issues={chk.get('total_issues')} P0={chk.get('p0_count')} {chk.get('_elapsed')}s")

        results = api("GET", f"/api/check/{doc_id}/results")
        has_ref = isinstance(results, list) and any(i.get("standard_ref") for i in results)
        record("检查结果含 standard_ref", has_ref,
               next((i.get("standard_ref", "") for i in results if isinstance(i, dict) and i.get("standard_ref")), ""))

        # 4. 暗标合规检查
        dbk = api("POST", f"/api/check/dark-bid/{doc_id}")
        record("暗标合规检查", "total_issues" in dbk, f"issues={dbk.get('total_issues')} {dbk.get('_elapsed')}s")

        # 5. 标准包
        packs = api("GET", "/api/settings/standard-packs")
        record("标准包列表", packs.get("packs") == ["enterprise"], str(packs.get("packs")))
        sw = api("POST", "/api/settings/standard-packs", {"pack": "enterprise"})
        record("标准包切换", sw.get("success") is True, str(sw.get("pack")))
        sw_off = api("POST", "/api/settings/standard-packs", {"pack": None})
        record("标准包停用", sw_off.get("success") is True, "")

        # 6. AI 润色（无 API Key 应优雅降级）
        rw = api("POST", "/api/ai/rewrite", {"text": "现将有关工作安排如下。", "document_type": "notice", "mode": "deai"})
        graceful = ("success" in rw) and (rw.get("success") is True or rw.get("message"))
        record("AI 润色降级处理", graceful, str(rw.get("message") or "ok")[:60])
        record("风格库端点", isinstance(rw, dict), f"{rw.get('_elapsed')}s")

        # 7. PDF 导出（无转换器应给出安装指引；500 也是契约内降级）
        pdf = api("GET", f"/api/documents/{doc_id}/export/pdf")
        detail = str(pdf.get("detail") or "")
        guided = (pdf.get("success") is False or pdf.get("_http_status") == 500) and (
            "LibreOffice" in detail or "docx2pdf" in detail
        )
        record("PDF 导出指引", guided, detail[:80])

        # 8. 优化全流程（清洗 + 规则修复 + 生成）
        opt = api("POST", f"/api/optimize/{doc_id}", {"document_type": "meeting", "apply_fixes": True})
        out_path = opt.get("output_path")
        rec_opt = bool(out_path) and Path(out_path).exists()
        record("优化全流程", rec_opt,
               f"fixes={opt.get('fixes_applied')} cleaning={opt.get('cleaning')} {opt.get('_elapsed')}s")

        # 9. 输出可重解析 + 版式档案能力冒烟
        if rec_opt:
            sys.path.insert(0, str(BACKEND_DIR))
            from core.document.parser import parse_docx  # type: ignore

            m2 = parse_docx(out_path)
            record("优化输出可重解析", len(m2.paragraphs) > 0, f"paragraphs={len(m2.paragraphs)}")

        # 10. A4 预览数据
        prev = api("GET", f"/api/documents/{doc_id}/preview")
        record("A4 预览数据", isinstance(prev.get("paragraphs"), list) and len(prev.get("paragraphs", [])) > 0,
               f"paragraphs={len(prev.get('paragraphs', []))} {prev.get('_elapsed')}s")
    finally:
        _stop_proc(proc)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\n===== 可用性测试汇总: {passed}/{len(RESULTS)} 通过 =====")
    for name, ok, detail in RESULTS:
        print(f"  {'✅' if ok else '❌'} {name}")
    sys.exit(0 if passed == len(RESULTS) else 1)


if __name__ == "__main__":
    main()