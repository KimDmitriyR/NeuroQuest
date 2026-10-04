"""Windows-only asyncio fix.

asyncpg can fail to connect on Windows with:
    OSError: [WinError 64] Указанное сетевое имя более недоступно
    asyncpg.exceptions.ConnectionDoesNotExistError: connection was closed
    in the middle of operation

This is a known incompatibility between asyncpg and the default
ProactorEventLoop on Windows. Switching to SelectorEventLoop avoids it.
(SelectorEventLoop can't spawn subprocesses via asyncio, but this project
never does that, so it's a safe fix here.)

No-op on non-Windows platforms.
"""

import asyncio
import sys


def apply() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
