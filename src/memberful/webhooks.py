"""Memberful webhook handling utilities."""

import hashlib
import hmac
import json
from enum import Enum
from typing import Any, Callable, Optional

from pydantic import BaseModel

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


class WebhookEventType(Enum):
    """Supported Memberful webhook event types."""

    MEMBER_CREATED = 'member.created'
    MEMBER_UPDATED = 'member.updated'
    MEMBER_DEACTIVATED = 'member.deactivated'
    SUBSCRIPTION_CREATED = 'subscription.created'
    SUBSCRIPTION_UPDATED = 'subscription.updated'
    SUBSCRIPTION_EXPIRED = 'subscription.expired'
    SUBSCRIPTION_RENEWED = 'subscription.renewed'
    ORDER_COMPLETED = 'order.completed'
    ORDER_REFUNDED = 'order.refunded'


class WebhookPayload(BaseModel):
    """Base webhook payload structure."""

    event: str
    data: dict[str, Any]
    timestamp: int

    @property
    def event_type(self) -> Optional[WebhookEventType]:
        """Get the event type as an enum."""
        try:
            return WebhookEventType(self.event)
        except ValueError:
            return None


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
    if event_type == 'member_signup':
        return MemberSignupEvent(**payload)
    elif event_type == 'member_updated':
        return MemberUpdatedEvent(**payload)
    elif event_type == 'subscription.created':
        return SubscriptionCreatedEvent(**payload)
    elif event_type == 'subscription.updated':
        return SubscriptionUpdatedEvent(**payload)
    elif event_type == 'order.completed':
        return OrderCompletedEvent(**payload)
    elif event_type == 'order.suspended':
        return OrderSuspendedEvent(**payload)
    elif event_type == 'subscription_plan.created':
        return SubscriptionPlanCreatedEvent(**payload)
    elif event_type == 'subscription_plan.updated':
        return SubscriptionPlanUpdatedEvent(**payload)
    elif event_type == 'subscription_plan.deleted':
        return SubscriptionPlanDeletedEvent(**payload)
    elif event_type == 'download.created':
        return DownloadCreatedEvent(**payload)
    elif event_type == 'download.updated':
        return DownloadUpdatedEvent(**payload)
    elif event_type == 'download.deleted':
        return DownloadDeletedEvent(**payload)
    else:
        raise ValueError(f'Unsupported event type: {event_type}')


class WebhookHandler:
    """Handler for Memberful webhooks."""

    def __init__(self, secret_key: Optional[str] = None):
        """Initialize the webhook handler.

        Args:
            secret_key: Optional webhook secret key for signature verification
        """
        self.secret_key = secret_key
        self._event_handlers: dict[WebhookEventType, list[Callable[[dict[str, Any]], None]]] = {}

    def register_handler(self, event_type: WebhookEventType, handler: Callable[[dict[str, Any]], None]):
        """Register a handler for a specific event type.

        Args:
            event_type: The webhook event type to handle
            handler: Function to call when this event is received
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    def on(self, event_type: WebhookEventType):
        """Decorator to register event handlers.

        Args:
            event_type: The webhook event type to handle

        Example:
            @webhook_handler.on(WebhookEventType.MEMBER_CREATED)
            def handle_new_member(data):
                print(f"New member: {data['email']}")
        """

        def decorator(func: Callable[[dict[str, Any]], None]):
            self.register_handler(event_type, func)
            return func

        return decorator

    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify the webhook signature.

        Args:
            payload: Raw webhook payload string
            signature: Signature from X-Memberful-Webhook-Signature header

        Returns:
            True if signature is valid, False otherwise
        """
        if not self.secret_key:
            raise ValueError('Secret key is required for signature verification')

        # Remove 'sha256=' prefix if present
        signature = signature.removeprefix('sha256=')

        expected_signature = hmac.new(
            self.secret_key.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature)

    def process_webhook(self, payload: str, signature: Optional[str] = None) -> WebhookPayload:
        """Process an incoming webhook payload.

        Args:
            payload: Raw webhook payload string
            signature: Optional signature for verification

        Returns:
            Parsed webhook payload

        Raises:
            ValueError: If signature verification fails or payload is invalid
        """
        # Verify signature if provided and secret key is configured
        if signature and self.secret_key:
            if not self.verify_signature(payload, signature):
                raise ValueError('Invalid webhook signature')

        # Parse the payload
        try:
            data = json.loads(payload)
            webhook_payload = WebhookPayload(**data)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f'Invalid webhook payload: {e}')

        # Call registered handlers
        event_type = webhook_payload.event_type
        if event_type and event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(webhook_payload.data)
                except Exception as e:
                    # Log error but don't fail the entire webhook processing
                    print(f'Error in webhook handler: {e}')

        return webhook_payload

    def handle_member_created(self, data: dict[str, Any]):
        """Default handler for member.created events - override this method."""
        pass

    def handle_subscription_created(self, data: dict[str, Any]):
        """Default handler for subscription.created events - override this method."""
        pass
