"""Pydantic models for parsing and validating Memberful webhook payloads.

This module provides comprehensive type-safe models for all Memberful webhook events,
including member signup, subscription changes, order updates, and plan modifications.
All models are designed to be permissive with optional fields to handle real-world
webhook data variations.
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class WebhookBaseModel(BaseModel):
    """Base class for all webhook-related models with extra data handling."""

    model_config = ConfigDict(extra='allow')

    @property
    def extras(self) -> dict[str, Any]:
        """Read-only access to any extra fields not defined in the model."""
        return getattr(self, '__pydantic_extra__', {})


class SignupMethod(str, Enum):
    """Member signup methods."""

    CHECKOUT = 'checkout'
    MANUAL = 'manual'
    API = 'api'
    IMPORT = 'import'


class OrderStatus(str, Enum):
    """Order status values."""

    COMPLETED = 'completed'
    SUSPENDED = 'suspended'
    PENDING = 'pending'
    CANCELLED = 'cancelled'


class RenewalPeriod(str, Enum):
    """Subscription renewal periods."""

    MONTHLY = 'monthly'
    YEARLY = 'yearly'
    QUARTERLY = 'quarterly'
    WEEKLY = 'weekly'


class IntervalUnit(str, Enum):
    """Subscription interval units."""

    MONTH = 'month'
    YEAR = 'year'
    QUARTER = 'quarter'
    WEEK = 'week'
    DAY = 'day'


class Address(WebhookBaseModel):
    """Member address information."""

    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class CreditCard(WebhookBaseModel):
    """Credit card information."""

    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    last_four: Optional[str] = None
    brand: Optional[str] = None


class TrackingParams(WebhookBaseModel):
    """UTM tracking parameters."""

    utm_term: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_source: Optional[str] = None
    utm_content: Optional[str] = None


class SubscriptionPlan(WebhookBaseModel):
    """Subscription plan details."""

    id: int
    name: str
    slug: str
    price: Optional[int] = None  # Price in smallest currency unit (cents)
    renewal_period: Optional[RenewalPeriod] = None
    interval_unit: Optional[IntervalUnit] = None
    interval_count: int = 1
    for_sale: bool = True
    type: Optional[str] = None  # Plan type (e.g., 'standard_plan')


class MemberSubscription(WebhookBaseModel):
    """Member subscription details."""

    active: bool
    created_at: int  # Unix timestamp
    expires: bool
    expires_at: Optional[int] = None  # Unix timestamp
    id: int
    in_trial_period: bool = False
    subscription: SubscriptionPlan
    trial_end_at: Optional[int] = None  # Unix timestamp
    trial_start_at: Optional[int] = None  # Unix timestamp


class Product(WebhookBaseModel):
    """Download/product information."""

    id: int
    name: str
    price: int  # Price in smallest currency unit (cents)
    slug: str
    for_sale: bool = True


class Member(WebhookBaseModel):
    """Member information."""

    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    username: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: int  # Unix timestamp
    signup_method: Optional[SignupMethod] = None
    stripe_customer_id: Optional[str] = None
    discord_user_id: Optional[str] = None
    unrestricted_access: bool = False

    # Nested objects
    address: Optional[Address] = None
    credit_card: Optional[CreditCard] = None
    tracking_params: Optional[TrackingParams] = None

    # Custom fields - can be any type
    custom_field: Optional[Any] = None


class DeletedMember(WebhookBaseModel):
    """Minimal member information for deleted member events."""

    id: int
    deleted: bool = True
    # Note: email, created_at, and other fields are not included
    # in member.deleted events as the member data is no longer available


class SubscriptionChanges(WebhookBaseModel):
    """Changes made to a subscription (for subscription.updated events)."""

    plan_id: Optional[list[int]] = None  # [old_value, new_value]
    expires_at: Optional[list[str]] = None  # [old_value, new_value] - ISO datetime strings
    autorenew: Optional[list[bool]] = None  # [old_value, new_value]
    active: Optional[list[bool]] = None
    price: Optional[list[int]] = None


class Order(WebhookBaseModel):
    """Order information."""

    uuid: str
    number: str
    total: int  # Total in smallest currency unit (cents)
    status: OrderStatus
    receipt: Optional[str] = None
    created_at: Optional[int] = None  # Unix timestamp

    # Related objects
    member: Member
    products: list[Product] = Field(default_factory=list)
    subscriptions: list[MemberSubscription] = Field(default_factory=list)


# Webhook Event Models


class MemberSignupEvent(WebhookBaseModel):
    """member_signup webhook event."""

    event: str = Field(..., pattern=r'^member_signup$')
    member: Member


class MemberUpdatedEvent(WebhookBaseModel):
    """member_updated webhook event."""

    event: str = Field(..., pattern=r'^member_updated$')
    member: Member
    products: list[Product] = Field(default_factory=list)
    subscriptions: list[MemberSubscription] = Field(default_factory=list)


class SubscriptionCreatedEvent(WebhookBaseModel):
    """subscription.created webhook event."""

    event: str = Field(..., pattern=r'^subscription\.created$')
    member: Optional[Member] = None
    products: list[Product] = Field(default_factory=list)
    subscriptions: list[MemberSubscription] = Field(default_factory=list)


class SubscriptionUpdatedEvent(WebhookBaseModel):
    """subscription.updated webhook event."""

    event: str = Field(..., pattern=r'^subscription\.updated$')
    member: Optional[Member] = None
    products: list[Product] = Field(default_factory=list)
    subscriptions: list[MemberSubscription] = Field(default_factory=list)
    changed: Optional[SubscriptionChanges] = None


class OrderCompletedEvent(WebhookBaseModel):
    """order.completed webhook event."""

    event: str = Field(..., pattern=r'^order\.completed$')
    order: Order


class OrderSuspendedEvent(WebhookBaseModel):
    """order.suspended webhook event."""

    event: str = Field(..., pattern=r'^order\.suspended$')
    order: Order


class SubscriptionPlanCreatedEvent(WebhookBaseModel):
    """subscription_plan.created webhook event."""

    event: str = Field(..., pattern=r'^subscription_plan\.created$')
    subscription: SubscriptionPlan


class SubscriptionPlanUpdatedEvent(WebhookBaseModel):
    """subscription_plan.updated webhook event."""

    event: str = Field(..., pattern=r'^subscription_plan\.updated$')
    subscription: SubscriptionPlan


class SubscriptionPlanDeletedEvent(WebhookBaseModel):
    """subscription_plan.deleted webhook event."""

    event: str = Field(..., pattern=r'^subscription_plan\.deleted$')
    subscription: SubscriptionPlan


class DownloadCreatedEvent(WebhookBaseModel):
    """download.created webhook event."""

    event: str = Field(..., pattern=r'^download\.created$')
    product: Product


class DownloadUpdatedEvent(WebhookBaseModel):
    """download.updated webhook event."""

    event: str = Field(..., pattern=r'^download\.updated$')
    product: Product


class DownloadDeletedEvent(WebhookBaseModel):
    """download.deleted webhook event."""

    event: str = Field(..., pattern=r'^download\.deleted$')
    product: Product


class MemberDeletedEvent(WebhookBaseModel):
    """member.deleted webhook event."""

    event: str = Field(..., pattern=r'^member\.deleted$')
    member: DeletedMember
    products: list[Product] = Field(default_factory=list)
    subscriptions: list[MemberSubscription] = Field(default_factory=list)


class SubscriptionActivatedEvent(WebhookBaseModel):
    """subscription.activated webhook event."""

    event: str = Field(..., pattern=r'^subscription\.activated$')
    member: Optional[Member] = None
    products: list[Product] = Field(default_factory=list)
    subscriptions: list[MemberSubscription] = Field(default_factory=list)


class SubscriptionDeletedEvent(WebhookBaseModel):
    """subscription.deleted webhook event."""

    event: str = Field(..., pattern=r'^subscription\.deleted$')
    member: Optional[Member] = None
    products: list[Product] = Field(default_factory=list)
    subscriptions: list[MemberSubscription] = Field(default_factory=list)


class SubscriptionRenewedEvent(WebhookBaseModel):
    """subscription.renewed webhook event."""

    event: str = Field(..., pattern=r'^subscription\.renewed$')
    member: Optional[Member] = None
    products: list[Product] = Field(default_factory=list)
    subscriptions: list[MemberSubscription] = Field(default_factory=list)


# Union type for all webhook events
WebhookEvent = (
    MemberSignupEvent
    | MemberUpdatedEvent
    | MemberDeletedEvent
    | SubscriptionCreatedEvent
    | SubscriptionUpdatedEvent
    | SubscriptionActivatedEvent
    | SubscriptionDeletedEvent
    | SubscriptionRenewedEvent
    | OrderCompletedEvent
    | OrderSuspendedEvent
    | SubscriptionPlanCreatedEvent
    | SubscriptionPlanUpdatedEvent
    | SubscriptionPlanDeletedEvent
    | DownloadCreatedEvent
    | DownloadUpdatedEvent
    | DownloadDeletedEvent
)
