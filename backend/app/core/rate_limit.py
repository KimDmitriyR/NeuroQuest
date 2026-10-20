import math
import time
from collections import defaultdict, deque
from collections.abc import Callable


class FailureLimiter:
    """Sliding-window counter of FAILED attempts, keyed by an arbitrary string.

    In-memory and per process: enough to stop password guessing against a
    single instance. With several workers/instances each keeps its own counts,
    so the effective limit is multiplied - move this to Redis if you scale out.
    """

    _SWEEP_EVERY = 1024  # calls between full clean-ups of idle keys

    def __init__(
        self,
        max_failures: int,
        window_seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self._clock = clock
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._calls = 0

    def _prune(self, key: str, now: float) -> deque[float]:
        events = self._events[key]
        while events and now - events[0] >= self.window_seconds:
            events.popleft()
        return events

    def retry_after(self, key: str) -> int:
        """Seconds until `key` may try again; 0 when it is not blocked."""
        now = self._clock()
        events = self._prune(key, now)
        if not events:
            self._events.pop(key, None)
            return 0
        if len(events) < self.max_failures:
            return 0
        return max(1, math.ceil(events[0] + self.window_seconds - now))

    def record_failure(self, key: str) -> None:
        now = self._clock()
        self._prune(key, now).append(now)
        self._calls += 1
        if self._calls % self._SWEEP_EVERY == 0:
            self._sweep(now)

    def reset(self, key: str) -> None:
        self._events.pop(key, None)

    def clear(self) -> None:
        self._events.clear()

    def _sweep(self, now: float) -> None:
        for key in list(self._events):
            if not self._prune(key, now):
                del self._events[key]
