"""Memberful Python client for webhooks and API."""

__version__ = '0.1.0'
__author__ = 'Michael Kennedy'

# Main exports
# Import webhooks submodule - this allows: import memberful.webhooks
from . import webhooks
from .client import MemberfulClient

# For backward compatibility, expose webhook functions at top level
from .webhooks import (
    DownloadCreatedEvent,
    DownloadDeletedEvent,
    DownloadUpdatedEvent,
    Member,
    MemberSignupEvent,
    MemberUpdatedEvent,
    Order,
    OrderCompletedEvent,
    OrderSuspendedEvent,
    Product,
    SubscriptionCreatedEvent,
    SubscriptionPlan,
    SubscriptionPlanCreatedEvent,
    SubscriptionPlanDeletedEvent,
    SubscriptionPlanUpdatedEvent,
    SubscriptionUpdatedEvent,
    WebhookEvent,
    parse_payload,
    validate_signature,
)

__all__ = [
    'MemberfulClient',
    'webhooks',  # Webhooks submodule
    'parse_payload',
    'validate_signature',
    'WebhookEvent',
    'MemberSignupEvent',
    'MemberUpdatedEvent',
    'SubscriptionCreatedEvent',
    'SubscriptionUpdatedEvent',
    'OrderCompletedEvent',
    'OrderSuspendedEvent',
    'SubscriptionPlanCreatedEvent',
    'SubscriptionPlanUpdatedEvent',
    'SubscriptionPlanDeletedEvent',
    'DownloadCreatedEvent',
    'DownloadUpdatedEvent',
    'DownloadDeletedEvent',
    'Member',
    'Order',
    'Product',
    'SubscriptionPlan',
]
