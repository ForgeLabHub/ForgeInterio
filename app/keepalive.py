"""Keep-alive для бесплатных хостингов, которые усыпляют приложение.

Запускается только при `KEEP_ALIVE_ENABLED=true` и не в тестах: в CI он не
должен ходить в сеть. Поток демонический — не мешает остановке процесса.
"""
from __future__ import annotations

import threading
import time

from .config import settings

INTERVAL_SECONDS = 300


def ping_once(url: str) -> int | None:
    import requests

    try:
        response = requests.get(f"{url}/", timeout=10)
    except Exception as exc:  # noqa: BLE001 — сеть может отказать как угодно
        print(f"❌ Keep-alive ping failed: {exc}")
        return None
    if response.status_code == 200:
        print(f"✅ Keep-alive ping successful: {url}")
    else:
        print(f"⚠️ Keep-alive ping warning: {response.status_code}")
    return response.status_code


def loop(url: str, interval: int = INTERVAL_SECONDS) -> None:
    while True:
        ping_once(url)
        time.sleep(interval)


def start_if_enabled() -> threading.Thread | None:
    config = settings()
    if not config.keep_alive_enabled or config.is_test:
        return None
    thread = threading.Thread(target=loop, args=(config.app_url,), daemon=True)
    thread.start()
    return thread
