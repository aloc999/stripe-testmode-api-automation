import pytest

from src.clients.stripe_client import StripeClient
from src.schemas.stripe import (
    BALANCE_SCHEMA,
    CUSTOMER_SCHEMA,
    DELETED_CUSTOMER_SCHEMA,
    ERROR_SCHEMA,
    LIST_SCHEMA,
    PAYMENT_INTENT_SCHEMA,
)
from src.utils.assertions import assert_json, assert_schema, assert_status


@pytest.mark.schema
@pytest.mark.smoke
def test_balance_matches_contract(stripe: StripeClient) -> None:
    response = stripe.get_balance()
    assert_status(response, 200)
    assert_schema(assert_json(response), BALANCE_SCHEMA)


@pytest.mark.schema
def test_customer_matches_contract(stripe: StripeClient, customer: dict) -> None:
    assert_schema(customer, CUSTOMER_SCHEMA)
    fetched = stripe.retrieve_customer(customer["id"])
    assert_status(fetched, 200)
    assert_schema(assert_json(fetched), CUSTOMER_SCHEMA)


@pytest.mark.schema
def test_customer_list_matches_contract(stripe: StripeClient) -> None:
    response = stripe.list_customers(limit=1)
    assert_status(response, 200)
    assert_schema(assert_json(response), LIST_SCHEMA)


@pytest.mark.schema
def test_payment_intent_matches_contract(stripe: StripeClient) -> None:
    response = stripe.create_payment_intent(amount=1500, currency="usd")
    assert_status(response, 200)
    assert_schema(assert_json(response), PAYMENT_INTENT_SCHEMA)


@pytest.mark.schema
@pytest.mark.negative
def test_error_envelope_matches_contract(stripe: StripeClient) -> None:
    response = stripe.create_payment_intent(currency="usd")
    assert_status(response, 400)
    assert_schema(assert_json(response), ERROR_SCHEMA)


@pytest.mark.schema
def test_deleted_customer_matches_contract(stripe: StripeClient, unique_email: str) -> None:
    created = stripe.create_customer(email=unique_email)
    assert_status(created, 200)
    deleted = stripe.delete_customer(created.json()["id"])
    assert_status(deleted, 200)
    assert_schema(assert_json(deleted), DELETED_CUSTOMER_SCHEMA)
