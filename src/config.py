"""Configuration manager. Secrets come from the environment, never from source."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _float(name: str, default: float) -> float:
    raw = os.getenv(name)
    return default if raw in (None, "") else float(raw)


@dataclass(frozen=True)
class Settings:
    secret_key: str
    base_url: str
    timeout_seconds: float
    max_response_ms: float
    auth_probe_url: str
    invalid_key: str

    @property
    def is_test_mode(self) -> bool:
        return self.secret_key.startswith("sk_test_")

    @property
    def is_live_stripe(self) -> bool:
        return "api.stripe.com" in self.base_url

    def redacted(self) -> dict[str, str | float | None]:
        return {
            "base_url": self.base_url,
            "timeout_seconds": self.timeout_seconds,
            "max_response_ms": self.max_response_ms,
            "secret_key": _mask(self.secret_key),
            "invalid_key": _mask(self.invalid_key),
            "auth_probe_url": self.auth_probe_url,
        }


def _mask(value: str) -> str:
    if len(value) <= 10:
        return "***"
    return f"{value[:7]}…{value[-4:]}"


def load_settings() -> Settings:
    key = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock").strip()
    if key.startswith("sk_live_"):
        raise RuntimeError(
            "A live Stripe key was provided. This suite is Test Mode only. "
            "Use an sk_test_ key from https://dashboard.stripe.com/test/apikeys"
        )
    return Settings(
        secret_key=key,
        base_url=os.getenv("STRIPE_BASE_URL", "https://api.stripe.com").rstrip("/"),
        timeout_seconds=_float("STRIPE_TIMEOUT_SECONDS", 10),
        max_response_ms=_float("STRIPE_MAX_RESPONSE_MS", 1000),
        auth_probe_url=os.getenv(
            "STRIPE_AUTH_PROBE_URL", "https://api.stripe.com/v1/balance"
        ),
        invalid_key=os.getenv(
            "STRIPE_INVALID_KEY", "sk_test_invalid_key_for_negative_tests"
        ),
    )
