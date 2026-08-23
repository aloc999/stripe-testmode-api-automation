import pytest

from src.clients.stripe_client import StripeClient
from src.config import Settings
from src.utils.assertions import assert_json, assert_status


@pytest.mark.positive
@pytest.mark.smoke
def test_test_mode_key_is_used(settings: Settings) -> None:
    assert settings.is_test_mode
    assert not settings.secret_key.startswith("sk_live_")


@pytest.mark.positive
@pytest.mark.smoke
def test_balance_returns_test_mode_funds(stripe: StripeClient) -> None:
    response = stripe.get_balance()
    assert_status(response, 200)
    body = assert_json(response)
    assert body["object"] == "balance"
    assert body["livemode"] is False
    assert isinstance(body["available"], list)


@pytest.mark.positive
def test_customer_can_be_created_and_retrieved(
    stripe: StripeClient,
    customer: dict,
    unique_email: str,
    require_stripe_cloud,
) -> None:
    assert customer["object"] == "customer"
    assert customer["email"] == unique_email
    assert customer["livemode"] is False
    assert customer["id"].startswith("cus_")

    fetched = stripe.retrieve_customer(customer["id"])
    assert_status(fetched, 200)
    body = assert_json(fetched)
    assert body["id"] == customer["id"]
    assert body["email"] == unique_email


@pytest.mark.positive
def test_created_customer_has_test_mode_identity(stripe: StripeClient, customer: dict) -> None:
    assert customer["object"] == "customer"
    assert customer["id"].startswith("cus_")
    assert customer["livemode"] is False


@pytest.mark.positive
def test_customer_list_includes_created_record(
    stripe: StripeClient, customer: dict, require_stripe_cloud
) -> None:
    response = stripe.list_customers(limit=10)
    assert_status(response, 200)
    body = assert_json(response)
    assert body["object"] == "list"
    ids = [item["id"] for item in body["data"]]
    assert customer["id"] in ids


@pytest.mark.positive
def test_payment_intent_is_created_in_requires_payment_method(
    stripe: StripeClient, customer: dict
) -> None:
    response = stripe.create_payment_intent(
        amount=2500,
        currency="usd",
        customer=customer["id"],
    )
    assert_status(response, 200)
    body = assert_json(response)
    assert body["object"] == "payment_intent"
    assert body["amount"] == 2500
    assert body["currency"] == "usd"
    assert body["customer"] == customer["id"]
    assert body["livemode"] is False
    assert body["status"] in {"requires_payment_method", "requires_confirmation", "requires_action"}

    fetched = stripe.retrieve_payment_intent(body["id"])
    assert_status(fetched, 200)
    assert fetched.json()["id"] == body["id"]


@pytest.mark.positive
def test_product_catalog_accepts_a_new_item(stripe: StripeClient) -> None:
    response = stripe.create_product(
        name="24Slides QA License",
        description="Automation fixture — safe to ignore",
    )
    assert_status(response, 200)
    body = assert_json(response)
    assert body["object"] == "product"
    assert body["name"] == "24Slides QA License"
    assert body["livemode"] is False
    assert body["id"].startswith("prod_")
