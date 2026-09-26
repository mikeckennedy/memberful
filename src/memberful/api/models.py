"""Pydantic models for Memberful API responses.

This module provides type-safe models for all Memberful API responses,
including members, subscriptions, plans, and paginated response structures.
Models are designed to be permissive with optional fields to handle real-world
API response variations.
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class APIBaseModel(BaseModel):
    """Base class for all API-related models with extra data handling."""

    model_config = ConfigDict(extra='allow')

    @property
    def extras(self) -> dict[str, Any]:
        """Read-only access to any extra fields not defined in the model."""
        return getattr(self, '__pydantic_extra__', {})


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


class SignupMethod(str, Enum):
    """Member signup methods."""

    CHECKOUT = 'checkout'
    MANUAL = 'manual'
    API = 'api'
    IMPORT = 'import'


class Plan(APIBaseModel):
    """Subscription plan information.

    `name` and `price` keep their long-standing field names even though Memberful's live schema
    (talkpython.memberful.com, introspected 2026-09-25) doesn't have a `price` field at all - only
    `priceCents` - and only keeps `name` as a deprecated alias for `label` ("Use pass { name }
    instead"). MEMBERFUL_PLAN_FIELDS_FRAGMENT in api/__init__.py selects `price: priceCents` (a
    GraphQL field alias) so this required field is always populated without changing the model's
    public shape. `renewal_period`, `description`, `created_at` and `updated_at` have no schema
    equivalent at all (confirmed via the same introspection, deprecated fields included) and stay
    Optional/always-None.
    """

    id: int
    name: str
    price: int  # Price in smallest currency unit (cents); selected as `price: priceCents`
    slug: Optional[str] = None
    renewal_period: Optional[RenewalPeriod] = Field(None, alias='renewalPeriod')
    interval_unit: Optional[IntervalUnit] = Field(None, alias='intervalUnit')
    interval_count: Optional[int] = Field(None, alias='intervalCount')
    for_sale: Optional[bool] = Field(None, alias='forSale')
    description: Optional[str] = None
    created_at: Optional[int] = Field(None, alias='createdAt')  # Unix timestamp
    updated_at: Optional[int] = Field(None, alias='updatedAt')  # Unix timestamp


class Subscription(APIBaseModel):
    """Subscription information."""

    id: int
    active: bool
    # Memberful's schema declares createdAt as a nullable Int, so this stays Optional rather than
    # required - the same over-strictness that made a missing/absent `price` crash Plan parsing.
    created_at: Optional[int] = Field(None, alias='createdAt')  # Unix timestamp
    activated_at: Optional[int] = Field(None, alias='activatedAt')  # Unix timestamp; trial -> paid, or signup
    expires: Optional[bool] = None
    expires_at: Optional[int] = Field(None, alias='expiresAt')  # Unix timestamp
    plan: Optional[Plan] = None
    # Populated when the query selects `member { ... }` on the subscription (get_subscriptions /
    # get_all_subscriptions). A forward reference: Member is defined later in this module and also
    # holds a list of Subscription, so the mutual reference is resolved by model_rebuild() below.
    member: Optional['Member'] = None
    in_trial_period: Optional[bool] = Field(None, alias='inTrialPeriod')
    trial_end_at: Optional[int] = Field(None, alias='trialEndAt')  # Unix timestamp
    trial_start_at: Optional[int] = Field(None, alias='trialStartAt')  # Unix timestamp
    autorenew: Optional[bool] = None
    # member_id, coupon_code, expires, in_trial_period and updated_at have no scalar equivalent on
    # Memberful's live Subscription type (confirmed via introspection, deprecated fields included):
    # there is no flat `memberId` or `couponCode`, only the relations `member { id }` and
    # `coupon { code }` (the latter is now reachable through `member` above but not `coupon_code`,
    # which would need a nested Coupon model to populate safely); `expires`, `inTrialPeriod` and
    # `updatedAt` simply don't exist. All stay Optional/always-None from the API client.
    member_id: Optional[int] = Field(None, alias='memberId')
    coupon_code: Optional[str] = Field(None, alias='couponCode')
    updated_at: Optional[int] = Field(None, alias='updatedAt')  # Unix timestamp


class Address(APIBaseModel):
    """Member address information."""

    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = Field(None, alias='postalCode')
    country: Optional[str] = None


class CreditCard(APIBaseModel):
    """Credit card information."""

    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    last_four: Optional[str] = None
    brand: Optional[str] = None


class TrackingParams(APIBaseModel):
    """UTM tracking parameters."""

    utm_term: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_source: Optional[str] = None
    utm_content: Optional[str] = None


class Member(APIBaseModel):
    """Member information from API responses."""

    id: int
    email: str
    # first_name, last_name, created_at, updated_at, signup_method, deactivated and confirmed_at
    # have no equivalent in Memberful's live GraphQL schema (verified by introspecting
    # talkpython.memberful.com on 2026-09-25, including deprecated fields - Member exposes only
    # `fullName`, not separate first/last name parts, and has no timestamp/status fields at all;
    # subscription status lives on Subscription.active instead). They can never be selected, so
    # they stay Optional and are always None from the API client. Kept for backwards compatibility
    # in case Memberful adds them later, and because webhook payloads (a different model) do carry
    # some of these.
    first_name: Optional[str] = Field(None, alias='firstName')
    last_name: Optional[str] = Field(None, alias='lastName')
    full_name: Optional[str] = Field(None, alias='fullName')
    username: Optional[str] = None
    phone_number: Optional[str] = Field(None, alias='phoneNumber')
    created_at: Optional[int] = Field(None, alias='createdAt')  # Unix timestamp
    updated_at: Optional[int] = Field(None, alias='updatedAt')  # Unix timestamp
    signup_method: Optional[SignupMethod] = Field(None, alias='signupMethod')
    stripe_customer_id: Optional[str] = Field(None, alias='stripeCustomerId')
    discord_user_id: Optional[str] = Field(None, alias='discordUserId')
    unrestricted_access: Optional[bool] = Field(None, alias='unrestrictedAccess')
    deactivated: Optional[bool] = None
    confirmed_at: Optional[int] = Field(None, alias='confirmedAt')  # Unix timestamp

    # Nested objects
    address: Optional[Address] = None
    # credit_card, tracking_params, custom_fields are not selected by MemberfulClient's queries and
    # stay None. Memberful's schema does expose `creditCard` and `customField` (singular), and a
    # generic `trackingParams: JSON` scalar with no fixed shape - but reaching them safely needs
    # alias fixes and, for trackingParams, a model that tolerates arbitrary keys rather than the
    # fixed utm_* fields below. Out of scope for this pass; tracked as a known gap, not a regression.
    credit_card: Optional[CreditCard] = None
    tracking_params: Optional[TrackingParams] = None
    subscriptions: Optional[list[Subscription]] = None

    # Custom fields - can be any type
    custom_fields: Optional[dict[str, Any]] = None
    custom_field: Optional[Any] = None


# Subscription.member is a forward reference to this class (defined above it in this module), so
# resolve it now that Member exists.
Subscription.model_rebuild()


class Product(APIBaseModel):
    """Download/product information."""

    id: int
    name: str
    price: int  # Price in smallest currency unit (cents)
    slug: str
    for_sale: Optional[bool] = None
    description: Optional[str] = None
    created_at: Optional[int] = None  # Unix timestamp
    updated_at: Optional[int] = None  # Unix timestamp


# Paginated response models


class MembersResponse(APIBaseModel):
    """One page of members from Memberful's cursor-based GraphQL API.

    To get the next page, pass `end_cursor` back as `after` while `has_next_page` is True.
    Memberful doesn't report totals, so `total_count` and `total_pages` are always None; they stay
    on the model for backwards compatibility. `current_page` echoes the deprecated `page` argument.
    """

    members: list[Member] = Field(default_factory=list)
    end_cursor: Optional[str] = None
    has_next_page: bool = False
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    current_page: Optional[int] = None
    per_page: Optional[int] = None


class SubscriptionsResponse(APIBaseModel):
    """One page of subscriptions from Memberful's cursor-based GraphQL API.

    To get the next page, pass `end_cursor` back as `after` while `has_next_page` is True.
    Memberful doesn't report totals, so `total_count` and `total_pages` are always None; they stay
    on the model for backwards compatibility. `current_page` echoes the deprecated `page` argument.
    """

    subscriptions: list[Subscription] = Field(default_factory=list)
    end_cursor: Optional[str] = None
    has_next_page: bool = False
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    current_page: Optional[int] = None
    per_page: Optional[int] = None


class PlansResponse(APIBaseModel):
    """Response model for paginated plans API."""

    plans: list[Plan] = Field(default_factory=list)
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    current_page: Optional[int] = None
    per_page: Optional[int] = None


class ProductsResponse(APIBaseModel):
    """Response model for paginated products API."""

    products: list[Product] = Field(default_factory=list)
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    current_page: Optional[int] = None
    per_page: Optional[int] = None


# Individual response models for single item APIs


class MemberResponse(APIBaseModel):
    """Response model for single member API."""

    member: Member


class SubscriptionResponse(APIBaseModel):
    """Response model for single subscription API."""

    subscription: Subscription


class PlanResponse(APIBaseModel):
    """Response model for single plan API."""

    plan: Plan


class ProductResponse(APIBaseModel):
    """Response model for single product API."""

    product: Product
