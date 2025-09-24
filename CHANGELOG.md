# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Enhanced
- **Improved webhook event documentation** (`memberful.webhooks.models`)
  - Enhanced docstrings for all webhook event classes with detailed descriptions
  - Added comprehensive usage guidance for each event type
  - Added missing webhook events: `tax_id.updated`, `custom_fields.updated`, `subscription.deactivated`, `order.purchased`, and `order.refunded`
  - Updated `WebhookEvent` union type to include all supported events

## [0.1.0] - 2025-01-27

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
