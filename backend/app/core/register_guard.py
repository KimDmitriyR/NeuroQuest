from app.core.config import settings
from app.core.rate_limit import FailureLimiter


class RegisterGuard:
    """Flood protection for POST /api/auth/register.

    One sliding-window counter per client IP. Unlike the login guard it counts
    EVERY attempt that reached the handler, successful or not (a 409 "email
    already registered" costs an attempt too, so the endpoint cannot be used to
    enumerate accounts for free). Attempts refused with 429 are not recorded,
    so the block ends one window after the last counted attempt.

    In memory and per process, like LoginGuard. Behind a reverse proxy or
    tunnel every visitor can share the proxy's IP unless uvicorn runs with
    --proxy-headers: raise REGISTER_MAX_PER_IP for such demos.
    """

    def __init__(self) -> None:
        self._limiter = FailureLimiter(
            settings.register_max_per_ip,
            settings.register_rate_limit_window_seconds,
        )

    def retry_after(self, ip: str) -> int:
        return self._limiter.retry_after(ip)

    def record_attempt(self, ip: str) -> None:
        self._limiter.record_failure(ip)  # the limiter just counts timestamps

    def clear(self) -> None:
        self._limiter.clear()


register_guard = RegisterGuard()
