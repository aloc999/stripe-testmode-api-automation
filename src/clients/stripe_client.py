"""Thin Stripe Test Mode client. Auth is HTTP Basic with the secret key."""

from __future__ import annotations

from typing import Any

import requests

from src.config import Settings

API_VERSION = "2024-06-20"


class StripeClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.session = requests.Session()
        self.session.auth = (settings.secret_key, "")
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Stripe-Version": API_VERSION,
                "User-Agent": "24Slides-QA-Automation/1.0 (stripe-test-mode)",
            }
        )

    def _url(self, path: str) -> str:
        return f"{self.settings.base_url}{path}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        api_key: str | None = None,
    ) -> requests.Response:
        auth = (api_key, "") if api_key is not None else self.session.auth
        return self.session.request(
            method,
            self._url(path),
            data=data,
            params=params,
            auth=auth,
            timeout=self.settings.timeout_seconds,
        )

    def get_balance(self, api_key: str | None = None) -> requests.Response:
        return self._request("GET", "/v1/balance", api_key=api_key)

    def create_customer(
        self,
        *,
        email: str | None = None,
        name: str | None = None,
        description: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> requests.Response:
        payload: dict[str, Any] = {}
        if email is not None:
            payload["email"] = email
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if metadata:
            for key, value in metadata.items():
                payload[f"metadata[{key}]"] = value
        return self._request("POST", "/v1/customers", data=payload)

    def retrieve_customer(self, customer_id: str) -> requests.Response:
        return self._request("GET", f"/v1/customers/{customer_id}")

    def list_customers(self, limit: int = 3) -> requests.Response:
        return self._request("GET", "/v1/customers", params={"limit": limit})

    def delete_customer(self, customer_id: str) -> requests.Response:
        return self._request("DELETE", f"/v1/customers/{customer_id}")

    def create_payment_intent(
        self,
        *,
        amount: int | None = None,
        currency: str | None = None,
        customer: str | None = None,
        automatic_payment_methods: bool = True,
    ) -> requests.Response:
        payload: dict[str, Any] = {}
        if amount is not None:
            payload["amount"] = amount
        if currency is not None:
            payload["currency"] = currency
        if customer is not None:
            payload["customer"] = customer
        if automatic_payment_methods:
            payload["automatic_payment_methods[enabled]"] = "true"
        return self._request("POST", "/v1/payment_intents", data=payload)

    def retrieve_payment_intent(self, intent_id: str) -> requests.Response:
        return self._request("GET", f"/v1/payment_intents/{intent_id}")

    def create_product(self, name: str, description: str | None = None) -> requests.Response:
        payload: dict[str, Any] = {"name": name}
        if description is not None:
            payload["description"] = description
        return self._request("POST", "/v1/products", data=payload)

    def list_products(self, limit: int = 3) -> requests.Response:
        return self._request("GET", "/v1/products", params={"limit": limit})
