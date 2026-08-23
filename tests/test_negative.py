import pytest

from src.clients.stripe_client import StripeClient
from src.utils.assertions import assert_json, assert_status


@pytest.mark.negative
def test_missing_payment_intent_amount_is_rejected(stripe: StripeClient) -> None:
    response = stripe.create_payment_intent(currency="usd")
    assert_status(response, 400)
    body = assert_json(response)
    assert body["error"]["type"] == "invalid_request_error"
    assert body["error"].get("param") in {"amount", None} or "amount" in body["error"]["message"].lower()


@pytest.mark.negative
def test_missing_payment_intent_currency_is_rejected(stripe: StripeClient) -> None:
    response = stripe.create_payment_intent(amount=2000, currency=None)
    assert_status(response, 400)
    body = assert_json(response)
    assert body["error"]["type"] == "invalid_request_error"


@pytest.mark.negative
def test_invalid_currency_is_rejected(stripe: StripeClient, require_stripe_cloud) -> None:
    response = stripe.create_payment_intent(amount=2000, currency="zzz")
    assert_status(response, 400)
    body = assert_json(response)
    assert body["error"]["type"] == "invalid_request_error"
    assert "currency" in body["error"]["message"].lower() or body["error"].get("param") == "currency"


@pytest.mark.negative
def test_unknown_customer_returns_not_found(stripe: StripeClient, require_stripe_cloud) -> None:
    response = stripe.retrieve_customer("cus_doesnotexist24slides")
    assert_status(response, 404)
    body = assert_json(response)
    assert body["error"]["type"] == "invalid_request_error"


@pytest.mark.negative
def test_customer_can_be_deleted(stripe: StripeClient, unique_email: str) -> None:
    created = stripe.create_customer(email=unique_email, name="To Delete")
    assert_status(created, 200)
    customer_id = created.json()["id"]

    deleted = stripe.delete_customer(customer_id)
    assert_status(deleted, 200)
    body = assert_json(deleted)
    assert body["deleted"] is True
    assert body["id"] == customer_id
