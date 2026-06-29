# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
AI 模型可用性检测服务。

每 60 秒检测一次所有已配置的 AI provider，记录在线状态和延迟。
状态通过 /api/ai/status 端点暴露给前端。
"""
from __future__ import annotations

import asyncio
import time
from typing import Any
from dataclasses import dataclass, field

import httpx

from utils.logger import logger


@dataclass
class ProviderStatus:
    provider: str
    model: str
    base_url: str
    online: bool = False
    latency_ms: int = 0
    last_check: float = 0.0
    error: str = ""


# 全局状态存储
_provider_statuses: dict[str, ProviderStatus] = {}
_check_task: asyncio.Task | None = None
_CHECK_INTERVAL = 60  # 秒


def get_all_statuses() -> list[dict[str, Any]]:
    """获取所有 provider 的当前状态（供 API 调用）。"""
    return [
        {
            "provider": s.provider,
            "model": s.model,
            "base_url": s.base_url,
            "online": s.online,
            "latency_ms": s.latency_ms,
            "last_check": s.last_check,
            "error": s.error,
        }
        for s in _provider_statuses.values()
    ]


async def _check_provider(status: ProviderStatus, api_key: str) -> None:
    """检测单个 provider 的可用性。"""
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 使用 /models 端点做轻量检测（OpenAI 兼容接口）
            resp = await client.get(
                f"{status.base_url.rstrip('/')}/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            resp.raise_for_status()
            elapsed = int((time.monotonic() - start) * 1000)
            status.online = True
            status.latency_ms = elapsed
            status.error = ""
    except httpx.ConnectError:
        status.online = False
        status.error = "连接失败"
    except httpx.TimeoutException:
        status.online = False
        status.error = "超时"
    except httpx.HTTPStatusError as e:
        status.online = False
        status.error = f"HTTP {e.response.status_code}"
    except Exception as e:
        status.online = False
        status.error = str(e)[:80]
    finally:
        status.last_check = time.time()


async def _check_claude_provider(status: ProviderStatus, api_key: str) -> None:
    """检测 Claude provider（使用 Anthropic Messages API）。"""
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{status.base_url.rstrip('/')}/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": status.model,
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "hi"}],
                },
            )
            # 200 或 400 都说明接口可达
            if resp.status_code in (200, 400, 401, 429):
                elapsed = int((time.monotonic() - start) * 1000)
                status.online = resp.status_code != 401
                status.latency_ms = elapsed
                status.error = "" if status.online else "认证失败"
            else:
                status.online = False
                status.error = f"HTTP {resp.status_code}"
    except Exception as e:
        status.online = False
        status.error = str(e)[:80]
    finally:
        status.last_check = time.time()


async def _run_all_checks() -> None:
    """检测所有已配置的 AI provider。

    使用 asyncio.to_thread() 避免阻塞事件循环。
    """
    from db.database import SessionLocal
    from db.models import AIConfig
    from utils.crypto import decrypt_value

    # 使用线程池执行同步数据库操作
    def _db_check():
        db = SessionLocal()
        try:
            configs = db.query(AIConfig).filter(AIConfig.is_active == True).all()
            return configs
        finally:
            db.close()

    try:
        configs = await asyncio.to_thread(_db_check)
        if not configs:
            return

        for cfg in configs:
            # 解密 API key
            try:
                api_key = decrypt_value(cfg.api_key_encrypted) if cfg.api_key_encrypted else ""
            except Exception:
                api_key = ""

            if not api_key:
                continue

            # 更新或创建状态对象
            key = cfg.provider
            if key not in _provider_statuses:
                _provider_statuses[key] = ProviderStatus(
                    provider=cfg.provider,
                    model=cfg.model or "",
                    base_url=cfg.base_url or "",
                )
            else:
                _provider_statuses[key].model = cfg.model or ""
                _provider_statuses[key].base_url = cfg.base_url or ""

            status = _provider_statuses[key]

            # Claude 使用专用检测
            if cfg.provider == "claude":
                await _check_claude_provider(status, api_key)
            else:
                await _check_provider(status, api_key)

            logger.debug(
                f"Health check: {cfg.provider} → "
                f"{'✓' if status.online else '✗'} {status.latency_ms}ms {status.error}"
            )
    except Exception as e:
        logger.error(f"Model health check error: {e}")


async def start_health_checker() -> None:
    """启动后台健康检测循环。"""
    global _check_task

    async def _loop():
        while True:
            try:
                await _run_all_checks()
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
            await asyncio.sleep(_CHECK_INTERVAL)

    _check_task = asyncio.create_task(_loop())
    logger.info(f"Model health checker started (interval={_CHECK_INTERVAL}s)")


def stop_health_checker() -> None:
    """停止后台健康检测。"""
    global _check_task
    if _check_task and not _check_task.done():
        _check_task.cancel()
        _check_task = None
        logger.info("Model health checker stopped")
