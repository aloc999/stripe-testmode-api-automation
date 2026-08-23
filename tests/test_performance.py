import pytest

from src.clients.stripe_client import StripeClient
from src.config import Settings
from src.utils.assertions import assert_performance, assert_status, elapsed_ms


@pytest.mark.performance
@pytest.mark.smoke
@pytest.mark.parametrize(
    "label,call",
    [
        ("balance", lambda client: client.get_balance()),
        ("customers", lambda client: client.list_customers(limit=1)),
        ("products", lambda client: client.list_products(limit=1)),
    ],
    ids=["balance", "customers", "products"],
)
def test_read_endpoints_respond_within_budget(
    stripe: StripeClient, settings: Settings, label: str, call
) -> None:
    response = call(stripe)
    assert_status(response, 200)
    took = assert_performance(response, settings.max_response_ms)
    print(f"{label} responded in {took:.1f}ms (budget {settings.max_response_ms:.0f}ms)")


@pytest.mark.performance
def test_validation_errors_are_also_fast(
    stripe: StripeClient, settings: Settings
) -> None:
    response = stripe.create_payment_intent(currency="usd")
    assert response.status_code >= 400
    took = elapsed_ms(response)
    print(f"invalid currency responded in {took:.1f}ms")
    assert took < settings.max_response_ms
