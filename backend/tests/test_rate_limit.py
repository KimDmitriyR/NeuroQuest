import pytest

from app.core.rate_limit import FailureLimiter

EMAIL = "victim@example.com"
PASSWORD = "supersecret123"


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


# ------------------------------------------------------------- the limiter itself


def test_limiter_blocks_after_max_failures_and_reports_retry_after():
    clock = FakeClock()
    limiter = FailureLimiter(max_failures=3, window_seconds=60, clock=clock)

    for _ in range(2):
        limiter.record_failure("k")
    assert limiter.retry_after("k") == 0

    limiter.record_failure("k")
    assert limiter.retry_after("k") == 60
    clock.advance(25)
    assert limiter.retry_after("k") == 35


def test_limiter_forgets_failures_after_the_window():
    clock = FakeClock()
    limiter = FailureLimiter(max_failures=2, window_seconds=60, clock=clock)
    limiter.record_failure("k")
    limiter.record_failure("k")
    assert limiter.retry_after("k") > 0

    clock.advance(60)
    assert limiter.retry_after("k") == 0


def test_limiter_window_slides_instead_of_resetting_all_at_once():
    clock = FakeClock()
    limiter = FailureLimiter(max_failures=2, window_seconds=60, clock=clock)
    limiter.record_failure("k")  # t=0
    clock.advance(40)
    limiter.record_failure("k")  # t=40 -> blocked
    clock.advance(20)  # t=60: the first one expired, the second has not
    assert limiter.retry_after("k") == 0
    limiter.record_failure("k")
    assert limiter.retry_after("k") == 40


def test_limiter_keys_are_independent_and_reset_works():
    limiter = FailureLimiter(max_failures=1, window_seconds=60, clock=FakeClock())
    limiter.record_failure("a")
    assert limiter.retry_after("a") > 0
    assert limiter.retry_after("b") == 0

    limiter.reset("a")
    assert limiter.retry_after("a") == 0


def test_limiter_does_not_grow_without_bound():
    clock = FakeClock()
    limiter = FailureLimiter(max_failures=5, window_seconds=60, clock=clock)
    for i in range(3000):
        limiter.record_failure(f"ip-{i}")
    clock.advance(61)
    for i in range(FailureLimiter._SWEEP_EVERY):
        limiter.record_failure("fresh")
    assert len(limiter._events) <= 2  # the 3000 idle keys were swept away


# ------------------------------------------------------------- the endpoint


async def _register(client, email=EMAIL):
    response = await client.post(
        "/api/auth/register",
        json={"email": email, "password": PASSWORD, "accept_terms": True},
    )
    assert response.status_code == 201


async def _login(client, password, email=EMAIL):
    return await client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )


async def test_login_is_blocked_after_repeated_failures_even_with_right_password(client):
    await _register(client)

    for _ in range(5):
        assert (await _login(client, "wrong-password")).status_code == 401

    blocked = await _login(client, PASSWORD)
    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) > 0


async def test_blocked_login_does_not_even_check_the_password(client, monkeypatch):
    await _register(client)
    for _ in range(5):
        await _login(client, "wrong-password")

    def explode(*_a, **_k):
        raise AssertionError("bcrypt must not run for a blocked client")

    monkeypatch.setattr("app.services.auth_service.verify_password", explode)
    assert (await _login(client, PASSWORD)).status_code == 429


async def test_a_few_typos_do_not_block_and_success_forgives_them(client):
    await _register(client)

    for _ in range(4):
        assert (await _login(client, "typo")).status_code == 401
    assert (await _login(client, PASSWORD)).status_code == 200

    # the counter was cleared by the success: four more typos are fine again
    for _ in range(4):
        assert (await _login(client, "typo")).status_code == 401
    assert (await _login(client, PASSWORD)).status_code == 200


async def test_unknown_email_is_throttled_too(client):
    for _ in range(5):
        assert (await _login(client, "x", email="ghost@example.com")).status_code == 401
    assert (await _login(client, "x", email="ghost@example.com")).status_code == 429


async def test_email_is_normalised_so_case_tricks_do_not_dodge_the_limit(client):
    await _register(client)
    variants = ["victim@example.com", "VICTIM@example.com", "Victim@Example.com"]
    for i in range(5):
        await _login(client, "nope", email=variants[i % 3])

    assert (await _login(client, PASSWORD, email="VICTIM@EXAMPLE.COM")).status_code == 429


async def test_one_ip_spraying_many_accounts_gets_blocked(client):
    # each account stays under its own limit, but the IP as a whole does not
    for i in range(20):
        response = await _login(client, "x", email=f"user{i}@example.com")
        assert response.status_code == 401

    assert (await _login(client, "x", email="fresh@example.com")).status_code == 429


async def test_other_accounts_work_normally_while_one_is_throttled(client):
    await _register(client, "victim@example.com")
    await _register(client, "bystander@example.com")
    for _ in range(5):
        await _login(client, "wrong")

    assert (await _login(client, PASSWORD)).status_code == 429
    ok = await _login(client, PASSWORD, email="bystander@example.com")
    assert ok.status_code == 200


async def test_lockout_expires(client, monkeypatch):
    from app.core import login_guard as module

    clock = FakeClock()
    for limiter in (
        module.login_guard._pair,
        module.login_guard._ip,
        module.login_guard._email,
    ):
        monkeypatch.setattr(limiter, "_clock", clock)

    await _register(client)
    for _ in range(5):
        await _login(client, "wrong")
    assert (await _login(client, PASSWORD)).status_code == 429

    clock.advance(15 * 60)
    assert (await _login(client, PASSWORD)).status_code == 200


# ------------------------------------------------------------- registration limit


async def _try_register(client, email, *, password=PASSWORD, accept_terms=True):
    return await client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "accept_terms": accept_terms},
    )


async def test_register_is_blocked_after_ten_attempts_from_one_ip(client):
    for i in range(10):
        assert (await _try_register(client, f"p{i}@example.com")).status_code == 201

    blocked = await _try_register(client, "p10@example.com")
    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) > 0


async def test_register_409_counts_as_an_attempt(client):
    await _register(client)  # attempt 1 (201)
    for _ in range(9):  # attempts 2..10, all "already registered"
        assert (await _try_register(client, EMAIL)).status_code == 409

    assert (await _try_register(client, EMAIL)).status_code == 429
    # and the rest of the world is blocked too, not only the repeated email
    assert (await _try_register(client, "other@example.com")).status_code == 429


async def test_register_422_does_not_spend_attempts(client):
    for _ in range(15):
        assert (await _try_register(client, "bad", password="x")).status_code == 422
        assert (await _try_register(client, "a@example.com", accept_terms=False)).status_code == 422

    assert (await _try_register(client, "fine@example.com")).status_code == 201


async def test_register_limit_is_configurable(client, monkeypatch):
    from app.core.register_guard import register_guard

    monkeypatch.setattr(register_guard._limiter, "max_failures", 2)
    assert (await _try_register(client, "a@example.com")).status_code == 201
    assert (await _try_register(client, "b@example.com")).status_code == 201
    assert (await _try_register(client, "c@example.com")).status_code == 429


async def test_register_block_expires_after_the_window(client, monkeypatch):
    from app.core.register_guard import register_guard

    clock = FakeClock()
    monkeypatch.setattr(register_guard._limiter, "_clock", clock)
    for i in range(10):
        await _try_register(client, f"p{i}@example.com")
    assert (await _try_register(client, "late@example.com")).status_code == 429

    clock.advance(60 * 60)
    assert (await _try_register(client, "late@example.com")).status_code == 201


async def test_blocked_register_does_not_extend_the_block(client, monkeypatch):
    from app.core.register_guard import register_guard

    clock = FakeClock()
    monkeypatch.setattr(register_guard._limiter, "_clock", clock)
    for i in range(10):
        await _try_register(client, f"p{i}@example.com")
    clock.advance(30 * 60)
    assert (await _try_register(client, "x@example.com")).status_code == 429  # refused, not counted

    clock.advance(30 * 60)  # the window since the 10 real attempts is over
    assert (await _try_register(client, "x@example.com")).status_code == 201


async def test_registration_limit_does_not_affect_login(client):
    await _register(client)
    for i in range(9):
        await _try_register(client, f"p{i}@example.com")
    assert (await _try_register(client, "z@example.com")).status_code == 429
    assert (await _login(client, PASSWORD)).status_code == 200
