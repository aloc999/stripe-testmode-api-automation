# Stripe Test Mode API Automation — Pytest + Requests

Task 2 of the 24Slides QA Automation assessment.

Python API suite against [Stripe Test Mode](https://docs.stripe.com/keys#test-live-modes): customers, payment intents, products, and balance. Live keys (`sk_live_`) are rejected by the config manager. Secrets stay in `.env` and are never logged.

## Why Stripe Test Mode

It is an allowed Task 2 target, it requires real credential handling, and Test Mode lets the suite create and delete objects without moving money.

## Architecture

```
src/
  config.py                 ← .env manager; refuses sk_live_
  clients/stripe_client.py  ← one client, HTTP Basic auth
  schemas/stripe.py         ← jsonschema contracts
  utils/assertions.py
tests/
  test_positive.py
  test_negative.py
  test_schema.py
  test_performance.py
  test_auth.py              ← 401 against api.stripe.com
docker-compose.yml          ← optional stripe-mock
```

## Prerequisites

- Python 3.11+
- A Stripe **test** secret key (`sk_test_…`) from [Dashboard → Test mode → API keys](https://dashboard.stripe.com/test/apikeys)
- Optional: Docker, if you want to run against [stripe-mock](https://github.com/stripe/stripe-mock) instead of Stripe's cloud

## Setup

```bash
git clone https://github.com/aloc999/stripe-testmode-api-automation.git
cd stripe-testmode-api-automation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# paste your sk_test_ key into .env
```

Required packages:

| Package | Role |
| --- | --- |
| `requests` | HTTP client |
| `pytest` | Runner |
| `python-dotenv` | `.env` loading |
| `jsonschema` | Payload contracts |
| `pytest-html` | Self-contained HTML report |
| `pytest-xdist` | Parallel workers |
| `pytest-timeout` | Hung-call guard |

**Never commit `.env`.**

## How to run

Against Stripe Test Mode (default):

```bash
pytest
pytest -m smoke
pytest -m "positive or schema"
```

`stripe-mock` returns canned fixtures (it does not persist customers or reject `zzz` currency). Cloud-only cases are skipped automatically. Against a local mock:

```bash
docker compose up -d
STRIPE_BASE_URL=http://127.0.0.1:12111 STRIPE_SECRET_KEY=sk_test_mock pytest
```

Invalid-key tests always call `https://api.stripe.com` so the 401 is Stripe's.

## Report

```
reports/report.html
```

## Coverage

| Layer | What is asserted |
| --- | --- |
| Positive | Test-mode balance; create/retrieve/list customer; PaymentIntent $25.00 USD; create product |
| Negative | Missing amount/currency (400), invalid currency (400), unknown customer (404), delete customer |
| Schema | Balance, customer, list, PaymentIntent, error envelope, deleted customer |
| Performance | Core GETs complete under `STRIPE_MAX_RESPONSE_MS` (default 1000ms) |
| Auth | Config redaction; live keys refused; Stripe 401 for invalid and missing keys |

## Design notes for reviewers

- **One client.** Tests never build URLs or attach keys themselves.
- **Test Mode hard-stop.** `load_settings()` raises if `STRIPE_SECRET_KEY` starts with `sk_live_`.
- **Cleanup.** The `customer` fixture deletes the customer it created.
- **401 is live.** Auth failures are not mocked.
- **Worker count vs. response-time budget:** `pytest.ini` defaults to `-n auto`, using all available CPU cores. Running many concurrent requests against Stripe's API from a location with higher network latency can occasionally push an individual read close to `STRIPE_MAX_RESPONSE_MS`. For a more conservative, stable run:
```bash
python -m pytest -n 2
```
The budget itself (1000ms default) is left unchanged — this is a concurrency/network note, not a threshold adjustment.


## License

MIT
