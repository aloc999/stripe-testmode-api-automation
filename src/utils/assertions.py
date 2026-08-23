from __future__ import annotations

import jsonschema
import requests


def assert_status(response: requests.Response, expected: int) -> None:
    assert response.status_code == expected, (
        f"Expected HTTP {expected}, got {response.status_code}: {response.text[:400]}"
    )


def assert_json(response: requests.Response) -> dict | list:
    payload = response.json()
    assert isinstance(payload, (dict, list)), f"JSON payload was {type(payload)}"
    return payload


def assert_schema(payload: dict | list, schema: dict) -> None:
    jsonschema.validate(instance=payload, schema=schema)


def elapsed_ms(response: requests.Response) -> float:
    return response.elapsed.total_seconds() * 1000


def assert_performance(response: requests.Response, budget_ms: float) -> float:
    took = elapsed_ms(response)
    assert took < budget_ms, (
        f"Response took {took:.1f}ms, budget is {budget_ms:.0f}ms "
        f"({response.request.method} {response.url})"
    )
    return took
