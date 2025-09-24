"""Pydantic models for parsing and validating Memberful webhook payloads.

This module provides comprehensive type-safe models for all Memberful webhook events,
including member signup, subscription changes, order updates, and plan modifications.
All models are designed to be permissive with optional fields to handle real-world
webhook data variations.
"""

from enum import Enum
from typing import Any, Optional, Union

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
    price_cents: Optional[int] = None  # Alternative field name used in webhooks
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


class Subscription(WebhookBaseModel):
    """Subscription details for webhook events."""

    id: int
    active: bool
    autorenew: bool
    created_at: str  # ISO datetime string
    expires_at: str  # ISO datetime string
    member: Member
    subscription_plan: SubscriptionPlan
    trial_end_at: Optional[str] = None  # ISO datetime string
    trial_start_at: Optional[str] = None  # ISO datetime string


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


class MemberChanges(WebhookBaseModel):
    """Changes made to a member (for member_updated events)."""

    # Common member fields that can change - each is [old_value, new_value]
    email: Optional[list[str]] = None
    first_name: Optional[list[str]] = None
    last_name: Optional[list[str]] = None
    full_name: Optional[list[str]] = None
    username: Optional[list[str]] = None
    phone_number: Optional[list[str]] = None
    discord_user_id: Optional[list[str]] = None
    stripe_customer_id: Optional[list[str]] = None
    unrestricted_access: Optional[list[bool]] = None
    custom_field: Optional[list[Any]] = None  # Custom fields can be any type


class Order(WebhookBaseModel):
    """Order information."""

    uuid: str
    number: Optional[str] = None
    total: int  # Total in smallest currency unit (cents)
    status: OrderStatus
    receipt: Optional[str] = None
    created_at: Optional[Union[int, str]] = None  # Unix timestamp or ISO datetime string

    # Related objects (optional - not present in all webhook contexts)
    member: Optional[Member] = None
    products: list[Product] = Field(default_factory=list)
    subscriptions: list[MemberSubscription] = Field(default_factory=list)


# Webhook Event Models


class MemberSignupEvent(WebhookBaseModel):
    """member_signup webhook event.

    Sent when a new member account is created. Use this webhook to add new
    members to your app or to a third-party service.
    """

    event: str = Field(..., pattern=r'^member_signup$')
    member: Member


class MemberUpdatedEvent(WebhookBaseModel):
    """member_updated webhook event.

    Sent when a member's profile information is updated. Use this webhook to
    update a member's profile information in your app. This is not triggered
    when a member updates custom fields; use custom_fields.updated for that.
    """

    event: str = Field(..., pattern=r'^member_updated$')
    member: Member
    changed: Optional[MemberChanges] = None


class SubscriptionCreatedEvent(WebhookBaseModel):
    """subscription.created webhook event.

    Sent when a new subscription is added to a member's account, including
    purchases, gift activations, group additions, or manual creation by staff.
    Use this webhook to signal that a member has subscribed. Both group managers
    and members trigger this event; compare the two member IDs to tell them apart.
    """

    event: str = Field(..., pattern=r'^subscription\.created$')
    subscription: Subscription


class SubscriptionUpdatedEvent(WebhookBaseModel):
    """subscription.updated webhook event.

    Sent when a member's subscription is updated. To detect a plan change, check
    for plan_id in the changed object (first value old, second new). The same
    applies to other changed fields like autorenew.
    """

    event: str = Field(..., pattern=r'^subscription\.updated$')
    subscription: Subscription
    changed: Optional[SubscriptionChanges] = None


class OrderCompletedEvent(WebhookBaseModel):
    """order.completed webhook event.

    Sent when a suspended order is marked completed by staff.
    """

    event: str = Field(..., pattern=r'^order\.completed$')
    order: Order


class OrderSuspendedEvent(WebhookBaseModel):
    """order.suspended webhook event.

    Sent when an order is suspended by staff.
    """

    event: str = Field(..., pattern=r'^order\.suspended$')
    order: Order


class SubscriptionPlanCreatedEvent(WebhookBaseModel):
    """subscription_plan.created webhook event.

    Sent when a new plan is created.
    """

    event: str = Field(..., pattern=r'^subscription_plan\.created$')
    subscription: SubscriptionPlan


class SubscriptionPlanUpdatedEvent(WebhookBaseModel):
    """subscription_plan.updated webhook event.

    Sent when a plan is updated.
    """

    event: str = Field(..., pattern=r'^subscription_plan\.updated$')
    subscription: SubscriptionPlan


class SubscriptionPlanDeletedEvent(WebhookBaseModel):
    """subscription_plan.deleted webhook event.

    Sent when a plan is deleted.
    """

    event: str = Field(..., pattern=r'^subscription_plan\.deleted$')
    subscription: SubscriptionPlan


class DownloadCreatedEvent(WebhookBaseModel):
    """download.created webhook event.

    Sent when a download is created.
    """

    event: str = Field(..., pattern=r'^download\.created$')
    product: Product


class DownloadUpdatedEvent(WebhookBaseModel):
    """download.updated webhook event.

    Sent when a download is updated.
    """

    event: str = Field(..., pattern=r'^download\.updated$')
    product: Product


class DownloadDeletedEvent(WebhookBaseModel):
    """download.deleted webhook event.

    Sent when a download is deleted.
    """

    event: str = Field(..., pattern=r'^download\.deleted$')
    product: Product


class MemberDeletedEvent(WebhookBaseModel):
    """member.deleted webhook event.

    Sent when a member is deleted from your Memberful account. Use this webhook
    to remove the member from your app if they were deleted. It is uncommon to
    delete accounts; in most cases react to subscription.deactivated instead.
    """

    event: str = Field(..., pattern=r'^member\.deleted$')
    member: DeletedMember


class SubscriptionActivatedEvent(WebhookBaseModel):
    """subscription.activated webhook event.

    Sent when a suspended order is marked completed by staff and the subscription
    becomes active again. This is not for member-led reactivation of an expired
    subscription; use subscription.renewed for that.
    """

    event: str = Field(..., pattern=r'^subscription\.activated$')
    subscription: Subscription


class SubscriptionDeletedEvent(WebhookBaseModel):
    """subscription.deleted webhook event.

    Sent when staff delete a member's subscription from the dashboard. Use this
    webhook to remove access or update status.
    """

    event: str = Field(..., pattern=r'^subscription\.deleted$')
    subscription: Subscription


class SubscriptionRenewedEvent(WebhookBaseModel):
    """subscription.renewed webhook event.

    Sent when a member's subscription is renewed or when a returning member
    reactivates an old subscription. Use this webhook to renew access. The
    payload does not distinguish renewal vs reactivation; query the API for
    history if needed.
    """

    event: str = Field(..., pattern=r'^subscription\.renewed$')
    subscription: Subscription
    order: Order


class SubscriptionDeactivatedEvent(WebhookBaseModel):
    """subscription.deactivated webhook event.

    Sent when a subscription fails to renew, expires, or becomes inactive, and
    also when staff suspend an order making the subscription inactive. Use this
    webhook to remove access or update status when payment stops.
    """

    event: str = Field(..., pattern=r'^subscription\.deactivated$')
    subscription: Subscription


class OrderPurchasedEvent(WebhookBaseModel):
    """order.purchased webhook event.

    Sent when a member places an order or when staff manually add an order to a
    member's account. Not triggered for renewal payments. Gift purchases trigger
    this event, but no subscription is created until the recipient activates the
    gift. Use this webhook to notify your app of a purchase.
    """

    event: str = Field(..., pattern=r'^order\.purchased$')
    order: Order


class OrderRefundedEvent(WebhookBaseModel):
    """order.refunded webhook event.

    Sent when staff refund an order. Use this trigger to update your app when a
    refund is processed.
    """

    event: str = Field(..., pattern=r'^order\.refunded$')
    order: Order


# Union type for all webhook events
WebhookEvent = (
    MemberSignupEvent
    | MemberUpdatedEvent
    | MemberDeletedEvent
    | SubscriptionCreatedEvent
    | SubscriptionUpdatedEvent
    | SubscriptionRenewedEvent
    | SubscriptionActivatedEvent
    | SubscriptionDeactivatedEvent
    | SubscriptionDeletedEvent
    | OrderPurchasedEvent
    | OrderRefundedEvent
    | OrderCompletedEvent
    | OrderSuspendedEvent
    | SubscriptionPlanCreatedEvent
    | SubscriptionPlanUpdatedEvent
    | SubscriptionPlanDeletedEvent
    | DownloadCreatedEvent
    | DownloadUpdatedEvent
    | DownloadDeletedEvent
)
