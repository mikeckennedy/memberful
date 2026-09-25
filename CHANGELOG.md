# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **`MemberfulClient` sends the real package version in its User-Agent.** It was hard-coded as `memberful-python/0.1.0`, and it now uses `memberful.__version__`.

### Removed
- **mypy dropped from the `dev` extras**, along with the unused `[tool.mypy]` and `[tool.ruff]` sections in `pyproject.toml`. ty (`ty.toml`) and `ruff.toml` are the configs in use.

## [0.3.2] - 2026-09-24

### Added
- **`py.typed` marker (PEP 561)**, so type checkers use memberful's inline annotations and consumers no longer need their own stubs. The package now has the `Typing :: Typed` classifier, and a test checks that the marker ships.

### Fixed
- **Public API annotations completed now that they're read downstream:**
  - `MemberfulClient.__aenter__()` returns `MemberfulClient`, so `async with MemberfulClient(...) as client` gives a typed `client`.
  - `MemberfulClient.__init__()` and `close()` are annotated to return `None`.
  - `memberful.api` has an `__all__`, so `Member`, `Subscription`, `MembersResponse` and `SubscriptionsResponse` are public re-exports and pyright doesn't report them as private imports.
  - `WebhookEvent` is declared as an explicit `TypeAlias`.

## [0.3.1] - 2026-09-24

### Fixed
- **`order.refunded` webhooks now parse** (`memberful.webhooks`)
  - `OrderStatus` was missing `'refunded'`, so `parse_payload()` raised a `ValidationError` on Memberful's documented `order.refunded` payload. Endpoints then returned non-2xx responses, and Memberful retries those for up to 24 hours and deletes endpoints that are still failing 3 days later.
  - Added `OrderStatus.REFUNDED`. Memberful documents `completed`, `suspended`, and `refunded`. `pending` and `cancelled` are kept for backwards compatibility.
  - `Order.status` is now `OrderStatus | str`. Known values still parse to `OrderStatus`, and a status Memberful adds later is kept as the raw string instead of failing validation.
- **`Subscription.expires_at` is now optional** (`str | None`, default `None`), so subscriptions that never expire parse correctly.
- **Corrected the 0.2.0 notes:** `tax_id.updated` and `custom_fields.updated` were listed as added, but they were never modeled. They now raise `UnsupportedEventError`.

### Added
- **`subscription.reactivated` event** (`SubscriptionReactivatedEvent`), which Memberful introduced in August 2026 for members who reactivate a lapsed subscription. It has the same shape as `subscription.renewed`.
- **`UnsupportedEventError`**, raised by `parse_payload()` for event types this package doesn't model, such as `custom_fields.updated` and `tax_id.updated`. It subclasses `ValueError`, so existing handlers still work. Catch it and return a 2xx to acknowledge and ignore those events.

### Changed
- **Examples updated to match the current webhook models.** Subscription events carry a single `subscription` with its `subscription_plan`, and optional fields like `plan.price` and `order.member` are checked before use. The FastAPI example now acknowledges unsupported events with a 2xx.
- **README corrections:**
  - The API Quick Start now passes `base_url`.
  - The webhook Quick Start reads `event.subscription.member` for `SubscriptionCreatedEvent`.
  - Stale claims are fixed: `httpx2` instead of `httpx`, only the request timeout is configurable, and the test coverage figures.
- **Type checking with [ty](https://github.com/astral-sh/ty)** (`uvx ty check`), configured in `ty.toml`.

## [0.3.0] - 2026-06-04

### Changed
- **Migrated HTTP client from `httpx` to `httpx2`** (`memberful.api`)
  - Replaced the `httpx` dependency with `httpx2` (`httpx2>=2.0.0`), the Pydantic-stewarded, API-compatible continuation of `httpx` — authored by httpx's original author and maintained by Pydantic Services Inc.
  - Motivation: upstream `httpx` development has stalled (no release in over a year, with its issue tracker and discussions locked down), making it a growing maintenance and supply-chain risk for downstream projects. `httpx2` is an actively maintained, drop-in replacement.
  - Imports use `import httpx2 as httpx`, so the public API and behavior of `MemberfulClient` are unchanged — no migration is required for consumers of this package.
  - Updated the FastAPI webhook example to match (`webhook_tester.py`, `requirements.piptools`, and the compiled `requirements.txt`).

## [0.2.0] - 2025-09-24

### Enhanced
- **Comprehensive webhook example** (`examples/basic_webhook_usage.py`)
  - Expanded to handle all 17 available Memberful webhook event types
  - Added handlers for member_updated, subscription_updated, subscription_deactivated events
  - Added handlers for all order events (purchased, refunded, completed, suspended)
  - Added handlers for subscription plan events (created, updated, deleted)
  - Added handlers for download/product events (created, updated, deleted)
  - Updated match statement with organized event routing by category
  - Fixed existing subscription handlers to use correct data structure
  - Added comprehensive documentation and practical usage examples
  - Enhanced module documentation with complete event coverage details

- **Improved webhook event documentation** (`memberful.webhooks.models`)
  - Enhanced docstrings for all webhook event classes with detailed descriptions
  - Added comprehensive usage guidance for each event type
  - Added missing webhook events: `tax_id.updated`, `custom_fields.updated`, `subscription.deactivated`, `order.purchased`, and `order.refunded`
  - Updated `WebhookEvent` union type to include all supported events

## [0.1.0] - 2025-09-09

### Added
- **Async Memberful API client** (`memberful.api.MemberfulClient`)
  - Support for members and subscriptions endpoints with full pagination
  - Automatic retry logic with exponential backoff
  - Async context manager support for proper resource cleanup
  - Type-safe responses with comprehensive Pydantic models
  - Rate limiting consideration with configurable delays
- **Comprehensive webhook handling** (`memberful.webhooks`)
  - `parse_payload()` function for type-safe webhook parsing
  - `validate_signature()` function for webhook signature verification
  - Support for all documented webhook events: member, subscription, order, plan, and download events
  - Automatic event type mapping to appropriate Pydantic models
  - Support for member deletion, subscription activation/deletion/renewal events
- **Robust Pydantic models** for both API and webhook data
  - Type-safe parsing and validation with permissive field handling
  - Enum support for known values (signup methods, order statuses, renewal periods)
  - Optional fields with sensible defaults for real-world data variations
  - Extra field handling via `extras` property for forward compatibility
- **Clean package structure** with namespace-based access
  - Users access functionality via `memberful.api` and `memberful.webhooks` submodules
  - No top-level namespace pollution - explicit imports required
- **Complete example implementations**
  - Basic API usage with async/await patterns
  - Webhook processing with signature validation
  - FastAPI webhook server example with testing utilities
