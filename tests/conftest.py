from __future__ import annotations

import time
from collections.abc import Iterator

import pytest

from src.clients.stripe_client import StripeClient
from src.config import Settings, load_settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    return load_settings()


@pytest.fixture(scope="session")
def stripe(settings: Settings) -> StripeClient:
    return StripeClient(settings)


@pytest.fixture
def require_stripe_cloud(settings: Settings) -> None:
    if not settings.is_live_stripe:
        pytest.skip("Requires Stripe Test Mode at api.stripe.com (stripe-mock is canned)")


@pytest.fixture
def unique_email() -> str:
    return f"qa.auto+{int(time.time() * 1000)}@example.test"


@pytest.fixture
def customer(stripe: StripeClient, unique_email: str) -> Iterator[dict]:
    response = stripe.create_customer(
        email=unique_email,
        name="24Slides QA",
        description="Created by the Task 2 automation suite",
        metadata={"suite": "24slides-task2"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    yield body
    stripe.delete_customer(body["id"])
