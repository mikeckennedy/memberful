"""Memberful webhook handling utilities."""

import hashlib
import hmac
from typing import Any

from .webhook_models import (
    DownloadCreatedEvent,
    DownloadDeletedEvent,
    DownloadUpdatedEvent,
    MemberSignupEvent,
    MemberUpdatedEvent,
    OrderCompletedEvent,
    OrderSuspendedEvent,
    SubscriptionCreatedEvent,
    SubscriptionPlanCreatedEvent,
    SubscriptionPlanDeletedEvent,
    SubscriptionPlanUpdatedEvent,
    SubscriptionUpdatedEvent,
    WebhookEvent,
)


def parse_webhook_payload(payload: dict[str, Any]) -> WebhookEvent:
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
        >>> event = parse_webhook_payload(payload)
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
        case 'subscription.created':
            return SubscriptionCreatedEvent(**payload)
        case 'subscription.updated':
            return SubscriptionUpdatedEvent(**payload)
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


def validate_webhook_signature(payload: str, signature: str, secret_key: str) -> bool:
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
