from app.core.config import settings
from app.core.rate_limit import FailureLimiter


class LoginGuard:
    """Brute-force protection for the login endpoint.

    Three independent counters of FAILED logins, so that one noisy client
    cannot easily lock a real parent out, while guessing stays expensive:
      * (ip, email) - the strict one: the same client hammering one account
      * ip          - one client spraying many accounts
      * email       - a distributed attack on one account (loosest limit)
    A login is refused while ANY of them is exhausted.
    """

    def __init__(self) -> None:
        window = settings.login_rate_limit_window_seconds
        self._pair = FailureLimiter(settings.login_max_failures_per_ip_email, window)
        self._ip = FailureLimiter(settings.login_max_failures_per_ip, window)
        self._email = FailureLimiter(settings.login_max_failures_per_email, window)

    @staticmethod
    def _keys(ip: str, email: str) -> tuple[str, str, str]:
        email = email.strip().lower()
        return f"{ip}|{email}", ip, email

    def retry_after(self, ip: str, email: str) -> int:
        pair, ip_key, email_key = self._keys(ip, email)
        return max(
            self._pair.retry_after(pair),
            self._ip.retry_after(ip_key),
            self._email.retry_after(email_key),
        )

    def record_failure(self, ip: str, email: str) -> None:
        pair, ip_key, email_key = self._keys(ip, email)
        self._pair.record_failure(pair)
        self._ip.record_failure(ip_key)
        self._email.record_failure(email_key)

    def record_success(self, ip: str, email: str) -> None:
        # forgive the legit user's own typos; the ip/email counters keep running
        # so a successful login on an attacker's own account clears nothing else
        pair, _, _ = self._keys(ip, email)
        self._pair.reset(pair)

    def clear(self) -> None:
        for limiter in (self._pair, self._ip, self._email):
            limiter.clear()


login_guard = LoginGuard()
