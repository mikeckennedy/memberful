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
    """Subscription plan information."""

    id: int
    name: str
    price: int  # Price in smallest currency unit (cents)
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
    created_at: int = Field(alias='createdAt')  # Unix timestamp
    expires: Optional[bool] = None
    expires_at: Optional[int] = Field(None, alias='expiresAt')  # Unix timestamp
    plan: Optional[Plan] = None
    in_trial_period: Optional[bool] = Field(None, alias='inTrialPeriod')
    trial_end_at: Optional[int] = Field(None, alias='trialEndAt')  # Unix timestamp
    trial_start_at: Optional[int] = Field(None, alias='trialStartAt')  # Unix timestamp
    autorenew: Optional[bool] = None
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
    credit_card: Optional[CreditCard] = None
    tracking_params: Optional[TrackingParams] = None
    subscriptions: Optional[list[Subscription]] = None

    # Custom fields - can be any type
    custom_fields: Optional[dict[str, Any]] = None
    custom_field: Optional[Any] = None


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
    """Response model for paginated members API."""

    members: list[Member] = Field(default_factory=list)
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    current_page: Optional[int] = None
    per_page: Optional[int] = None


class SubscriptionsResponse(APIBaseModel):
    """Response model for paginated subscriptions API."""

    subscriptions: list[Subscription] = Field(default_factory=list)
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
