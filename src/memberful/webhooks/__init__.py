"""Memberful webhook handling utilities and models.

This module provides comprehensive webhook support for Memberful, including:
- Webhook payload parsing and validation
- Type-safe webhook event models
- Signature verification utilities

Usage:
    import memberful.webhooks

    # Parse webhook payload
    event = memberful.webhooks.parse_payload(payload_dict)

    # Validate webhook signature
    is_valid = memberful.webhooks.validate_webhook_signature(raw_payload, signature, secret)

    # Access models directly
    member = memberful.webhooks.Member(id=123, email="test@example.com")
"""

import hashlib
import hmac
from typing import Any

from .models import (
    Address,
    CreditCard,
    DeletedMember,
    DownloadCreatedEvent,
    DownloadDeletedEvent,
    DownloadUpdatedEvent,
    IntervalUnit,
    Member,
    MemberDeletedEvent,
    MemberSignupEvent,
    MemberSubscription,
    MemberUpdatedEvent,
    Order,
    OrderCompletedEvent,
    OrderStatus,
    OrderSuspendedEvent,
    Product,
    RenewalPeriod,
    SignupMethod,
    SubscriptionActivatedEvent,
    SubscriptionChanges,
    SubscriptionCreatedEvent,
    SubscriptionDeletedEvent,
    SubscriptionPlan,
    SubscriptionPlanCreatedEvent,
    SubscriptionPlanDeletedEvent,
    SubscriptionPlanUpdatedEvent,
    SubscriptionRenewedEvent,
    SubscriptionUpdatedEvent,
    TrackingParams,
    WebhookBaseModel,
    WebhookEvent,
)


def parse_payload(payload: dict[str, Any]) -> WebhookEvent:
    """Parse a webhook payload into the appropriate Pydantic model.

    This function takes a raw webhook payload dictionary and returns the appropriate
    strongly-typed webhook event model based on the event type.

    Args:
        payload: Parsed JSON webhook payload dictionary

    Returns:
        Parsed webhook event model (subclass of WebhookEvent)

    Raises:
        ValueError: If the payload format is invalid or event type is unsupported

    Example:
        >>> payload = {"event": "member_signup", "member": {...}, ...}
        >>> event = parse_payload(payload)
        >>> isinstance(event, MemberSignupEvent)
        True
    """
    event_type = payload.get('event')

    # Parse based on event type
    match event_type:
        case 'member_signup':
            return MemberSignupEvent(**payload)
        case 'member_updated':
            return MemberUpdatedEvent(**payload)
        case 'member.deleted':
            return MemberDeletedEvent(**payload)
        case 'subscription.created':
            return SubscriptionCreatedEvent(**payload)
        case 'subscription.updated':
            return SubscriptionUpdatedEvent(**payload)
        case 'subscription.activated':
            return SubscriptionActivatedEvent(**payload)
        case 'subscription.deleted':
            return SubscriptionDeletedEvent(**payload)
        case 'subscription.renewed':
            return SubscriptionRenewedEvent(**payload)
        case 'order.completed':
            return OrderCompletedEvent(**payload)
        case 'order.suspended':
            return OrderSuspendedEvent(**payload)
        case 'subscription_plan.created':
            return SubscriptionPlanCreatedEvent(**payload)
        case 'subscription_plan.updated':
            return SubscriptionPlanUpdatedEvent(**payload)
        case 'subscription_plan.deleted':
            return SubscriptionPlanDeletedEvent(**payload)
        case 'download.created':
            return DownloadCreatedEvent(**payload)
        case 'download.updated':
            return DownloadUpdatedEvent(**payload)
        case 'download.deleted':
            return DownloadDeletedEvent(**payload)
        case _:
            raise ValueError(f'Unsupported event type: {event_type}')


def validate_signature(payload: str, signature: str, secret_key: str) -> bool:
    """Validate the webhook signature.

    Args:
        payload: Raw webhook payload string
        signature: Signature from X-Memberful-Webhook-Signature header
        secret_key: Webhook secret key

    Returns:
        True if signature is valid, False otherwise
    """
    # Remove 'sha256=' prefix if present
    signature = signature.removeprefix('sha256=')

    expected_signature = hmac.new(secret_key.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


# Export all the models and functions for easy access
__all__ = [
    # Functions
    'parse_payload',
    'validate_signature',
    # Base models and types
    'WebhookBaseModel',
    'WebhookEvent',
    # Enums
    'SignupMethod',
    'OrderStatus',
    'RenewalPeriod',
    'IntervalUnit',
    # Core models
    'Address',
    'CreditCard',
    'TrackingParams',
    'SubscriptionPlan',
    'MemberSubscription',
    'Product',
    'Member',
    'DeletedMember',
    'SubscriptionChanges',
    'Order',
    # Event models
    'MemberSignupEvent',
    'MemberUpdatedEvent',
    'MemberDeletedEvent',
    'SubscriptionCreatedEvent',
    'SubscriptionUpdatedEvent',
    'SubscriptionActivatedEvent',
    'SubscriptionDeletedEvent',
    'SubscriptionRenewedEvent',
    'OrderCompletedEvent',
    'OrderSuspendedEvent',
    'SubscriptionPlanCreatedEvent',
    'SubscriptionPlanUpdatedEvent',
    'SubscriptionPlanDeletedEvent',
    'DownloadCreatedEvent',
    'DownloadUpdatedEvent',
    'DownloadDeletedEvent',
]
