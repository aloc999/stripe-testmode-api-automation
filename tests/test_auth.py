"""Credential contracts.

Positive tests use STRIPE_SECRET_KEY from .env (Test Mode).
Invalid / missing keys are proven against the real Stripe API so the 401
is Stripe's, not a mock.
"""

from __future__ import annotations

import pytest
import requests

from src.config import Settings
from src.utils.assertions import assert_json, assert_status


def test_settings_never_expose_raw_secrets(settings: Settings) -> None:
    view = settings.redacted()
    assert settings.secret_key not in str(view)
    assert settings.invalid_key not in str(view)
    assert "…" in str(view["secret_key"]) or view["secret_key"] == "***"


def test_live_keys_are_rejected_by_the_config_manager(monkeypatch) -> None:
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_live_this_must_never_run")
    from src.config import load_settings

    try:
        load_settings()
        raise AssertionError("live keys must be rejected")
    except RuntimeError as error:
        assert "Test Mode" in str(error)


@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.live
@pytest.mark.smoke
def test_invalid_api_key_is_rejected_by_stripe(settings: Settings) -> None:
    response = requests.get(
        settings.auth_probe_url,
        auth=(settings.invalid_key, ""),
        timeout=settings.timeout_seconds,
        headers={"Accept": "application/json"},
    )
    assert_status(response, 401)
    body = assert_json(response)
    assert body["error"]["type"] == "invalid_request_error"
    assert "invalid" in body["error"]["message"].lower() or body["error"].get("code") == "invalid_api_key"


@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.live
def test_missing_api_key_is_rejected_by_stripe(settings: Settings) -> None:
    response = requests.get(
        settings.auth_probe_url,
        timeout=settings.timeout_seconds,
        headers={"Accept": "application/json"},
    )
    assert_status(response, 401)
    body = assert_json(response)
    assert body["error"]["type"] == "invalid_request_error"
