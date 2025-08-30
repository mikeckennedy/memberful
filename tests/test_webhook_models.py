"""Tests for Pydantic webhook models."""

import json
from typing import Any

import pytest

from memberful.webhooks import (
    Address,
    CreditCard,
    DownloadCreatedEvent,
    Member,
    MemberSignupEvent,
    Product,
    SubscriptionPlan,
    SubscriptionPlanCreatedEvent,
    SubscriptionUpdatedEvent,
    TrackingParams,
)


class TestMemberModels:
    """Test member-related models."""

    def test_address_model(self):
        """Test Address model with partial data."""
        address_data = {
            'street': '123 Main St',
            'city': 'New York',
            'state': 'NY',
            'postal_code': '10001',
            'country': 'US',
        }
        address = Address.model_validate(address_data)
        assert address.street == '123 Main St'
        assert address.city == 'New York'

    def test_address_model_with_nulls(self):
        """Test Address model handles null values."""
        address_data = {
            'street': None,
            'city': 'New York',
            'state': None,
        }
        address = Address.model_validate(address_data)
        assert address.street is None
        assert address.city == 'New York'
        assert address.state is None
        assert address.postal_code is None  # Not provided, should default to None

    def test_credit_card_model(self):
        """Test CreditCard model."""
        cc_data = {'exp_month': 12, 'exp_year': 2025}
        cc = CreditCard.model_validate(cc_data)
        assert cc.exp_month == 12
        assert cc.exp_year == 2025
        assert cc.last_four is None

    def test_tracking_params_model(self):
        """Test TrackingParams model."""
        tracking_data = {
            'utm_source': 'google',
            'utm_medium': 'cpc',
            'utm_campaign': 'spring_sale',
        }
        tracking = TrackingParams.model_validate(tracking_data)
        assert tracking.utm_source == 'google'
        assert tracking.utm_term is None

    def test_member_model_complete(self):
        """Test Member model with complete data."""
        member_data = {
            'id': 123,
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'full_name': 'John Doe',
            'username': 'johndoe',
            'created_at': 1640995200,
            'signup_method': 'checkout',
            'unrestricted_access': False,
            'address': {
                'street': '123 Main St',
                'city': 'New York',
                'state': 'NY',
            },
            'credit_card': {'exp_month': 12, 'exp_year': 2025},
            'tracking_params': {'utm_source': 'google'},
        }
        member = Member.model_validate(member_data)
        assert member.id == 123
        assert member.email == 'test@example.com'
        assert member.address is not None
        assert member.address.street == '123 Main St'
        assert member.credit_card is not None
        assert member.credit_card.exp_month == 12

    def test_member_model_minimal(self):
        """Test Member model with minimal required data."""
        member_data = {'id': 123, 'email': 'test@example.com', 'created_at': 1640995200}
        member = Member.model_validate(member_data)
        assert member.id == 123
        assert member.email == 'test@example.com'
        assert member.first_name is None
        assert member.address is None
        assert member.unrestricted_access is False  # Should use default


class TestSubscriptionModels:
    """Test subscription-related models."""

    def test_subscription_plan_model(self):
        """Test SubscriptionPlan model."""
        plan_data = {
            'id': 1,
            'price': 1000,
            'name': 'Monthly Plan',
            'slug': 'monthly-plan',
            'renewal_period': 'monthly',
            'interval_unit': 'month',
            'interval_count': 1,
            'for_sale': True,
        }
        plan = SubscriptionPlan.model_validate(plan_data)
        assert plan.id == 1
        assert plan.price == 1000
        assert plan.renewal_period == 'monthly'
        assert plan.for_sale is True

    def test_product_model(self):
        """Test Product model."""
        product_data = {
            'id': 1,
            'name': 'Sample Download',
            'price': 500,
            'slug': 'sample-download',
            'for_sale': True,
        }
        product = Product.model_validate(product_data)
        assert product.id == 1
        assert product.name == 'Sample Download'
        assert product.for_sale is True


class TestWebhookEvents:
    """Test webhook event models."""

    def test_member_signup_event(self):
        """Test MemberSignupEvent parsing."""
        event_data = {
            'event': 'member_signup',
            'member': {
                'id': 123,
                'email': 'test@example.com',
                'created_at': 1640995200,
                'first_name': 'John',
                'unrestricted_access': False,
            },
        }
        event = MemberSignupEvent.model_validate(event_data)
        assert event.event == 'member_signup'
        assert event.member.id == 123
        assert event.member.email == 'test@example.com'

    def test_subscription_plan_created_event(self):
        """Test SubscriptionPlanCreatedEvent parsing."""
        event_data = {
            'event': 'subscription_plan.created',
            'subscription': {
                'id': 1,
                'price': 1000,
                'name': 'Monthly Plan',
                'slug': 'monthly-plan',
                'renewal_period': 'monthly',
                'interval_unit': 'month',
                'interval_count': 1,
                'for_sale': True,
            },
        }
        event = SubscriptionPlanCreatedEvent.model_validate(event_data)
        assert event.event == 'subscription_plan.created'
        assert event.subscription.name == 'Monthly Plan'

    def test_download_created_event(self):
        """Test DownloadCreatedEvent parsing."""
        event_data = {
            'event': 'download.created',
            'product': {
                'id': 1,
                'name': 'Sample Download',
                'price': 500,
                'slug': 'sample-download',
                'for_sale': True,
            },
        }
        event = DownloadCreatedEvent.model_validate(event_data)
        assert event.event == 'download.created'
        assert event.product.name == 'Sample Download'

    def test_subscription_updated_with_changes(self):
        """Test SubscriptionUpdatedEvent with changes section."""
        event_data: dict[str, Any] = {
            'event': 'subscription.updated',
            'member': {
                'id': 123,
                'email': 'test@example.com',
                'created_at': 1640995200,
            },
            'products': [],
            'subscriptions': [],
            'changed': {
                'plan_id': [42, 43],
                'expires_at': ['2023-01-01T00:00:00Z', '2023-02-01T00:00:00Z'],
                'autorenew': [False, True],
            },
        }
        event = SubscriptionUpdatedEvent.model_validate(event_data)
        assert event.event == 'subscription.updated'
        assert event.changed is not None
        assert event.changed.plan_id == [42, 43]
        assert event.changed.autorenew == [False, True]

    def test_event_validation_fails_with_wrong_type(self):
        """Test that event validation fails with wrong event type."""
        with pytest.raises(ValueError):
            MemberSignupEvent.model_validate(
                {'event': 'wrong_event', 'member': {'id': 1, 'email': 'test@example.com', 'created_at': 123}}
            )


class TestJsonCompatibility:
    """Test parsing real JSON examples from the documentation."""

    def test_parse_member_signup_json(self):
        """Test parsing the member_signup JSON from documentation."""
        json_data = """
        {
          "event": "member_signup",
          "member": {
            "address": {
              "street": "Street",
              "city": "City",
              "state": "State",
              "postal_code": "Postal code",
              "country": "City"
            },
            "created_at": 1756245496,
            "credit_card": {
              "exp_month": 1,
              "exp_year": 2040
            },
            "custom_field": "Custom field value",
            "discord_user_id": "000000000000000000",
            "email": "john.doe@example.com",
            "first_name": "John",
            "full_name": "John Doe",
            "id": 0,
            "last_name": "Doe",
            "phone_number": "555-12345",
            "signup_method": "checkout",
            "stripe_customer_id": "cus_00000",
            "tracking_params": {
              "utm_term": "shoes",
              "utm_campaign": "summer_sale",
              "utm_medium": "social",
              "utm_source": "instagram",
              "utm_content": "textlink"
            },
            "unrestricted_access": false,
            "username": "john_doe"
          }
        }
        """
        data = json.loads(json_data)
        event = MemberSignupEvent.model_validate(data)

        assert event.event == 'member_signup'
        assert event.member.email == 'john.doe@example.com'
        assert event.member.address is not None
        assert event.member.address.street == 'Street'
        assert event.member.tracking_params is not None
        assert event.member.tracking_params.utm_source == 'instagram'
        assert event.member.credit_card is not None
        assert event.member.credit_card.exp_year == 2040

    def test_parse_subscription_plan_created_json(self):
        """Test parsing subscription_plan.created JSON from documentation."""
        json_data = """
        {
          "event": "subscription_plan.created",
          "subscription": {
            "id": 0,
            "price": 1000,
            "name": "Sample plan",
            "slug": "0-sample-plan",
            "renewal_period": "monthly",
            "interval_unit": "month",
            "interval_count": 1,
            "for_sale": true
          }
        }
        """
        data = json.loads(json_data)
        event = SubscriptionPlanCreatedEvent.model_validate(data)

        assert event.event == 'subscription_plan.created'
        assert event.subscription.name == 'Sample plan'
        assert event.subscription.price == 1000
        assert event.subscription.renewal_period == 'monthly'


class TestExtraDataHandling:
    """Test that models can handle extra data without crashes."""

    def test_member_with_extra_data(self):
        """Test Member model accepts and stores extra fields."""
        member_data = {
            'id': 123,
            'email': 'test@example.com',
            'created_at': 1640995200,
            # Extra fields that might come from webhook
            'custom_metadata': {'source': 'referral', 'campaign': 'winter2023'},
            'internal_notes': 'VIP customer',
            'analytics_id': 'abc-123-def',
        }

        member = Member.model_validate(member_data)

        # Verify required fields work
        assert member.id == 123
        assert member.email == 'test@example.com'
        assert member.created_at == 1640995200

        # Verify extra data is accessible via extras property
        assert member.extras['custom_metadata'] == {'source': 'referral', 'campaign': 'winter2023'}
        assert member.extras['internal_notes'] == 'VIP customer'
        assert member.extras['analytics_id'] == 'abc-123-def'

    def test_webhook_event_with_extra_data(self):
        """Test webhook events can handle extra fields from Memberful."""
        event_data = {
            'event': 'member_signup',
            'member': {
                'id': 456,
                'email': 'user@test.com',
                'created_at': 1640995200,
            },
            # Extra fields that might be added by Memberful in future
            'webhook_version': '2.1',
            'delivery_attempt': 1,
            'timestamp': 1640995300,
            'metadata': {'region': 'us-east', 'service': 'webhook-v2'},
        }

        event = MemberSignupEvent.model_validate(event_data)

        # Verify core functionality works
        assert event.event == 'member_signup'
        assert event.member.id == 456
        assert event.member.email == 'user@test.com'

        # Verify extra data is stored and accessible via extras property
        assert event.extras['webhook_version'] == '2.1'
        assert event.extras['delivery_attempt'] == 1
        assert event.extras['timestamp'] == 1640995300
        assert event.extras['metadata'] == {'region': 'us-east', 'service': 'webhook-v2'}

    def test_nested_models_with_extra_data(self):
        """Test that nested models also handle extra data correctly."""
        address_data = {
            'street': '123 Main St',
            'city': 'New York',
            'state': 'NY',
            # Extra fields
            'apartment': '4B',
            'building_code': 'A1',
            'delivery_instructions': 'Ring twice',
        }

        address = Address.model_validate(address_data)

        # Verify standard fields
        assert address.street == '123 Main St'
        assert address.city == 'New York'
        assert address.state == 'NY'

        # Verify extra fields are stored and accessible via extras property
        assert address.extras['apartment'] == '4B'
        assert address.extras['building_code'] == 'A1'
        assert address.extras['delivery_instructions'] == 'Ring twice'

    def test_extras_property_behavior(self):
        """Test the extras property returns empty dict when no extras and is read-only."""
        # Test with no extra data
        member_data = {
            'id': 123,
            'email': 'test@example.com',
            'created_at': 1640995200,
        }
        member = Member.model_validate(member_data)

        # Should return empty dict when no extras
        assert member.extras == {}

        # Test with extra data
        member_with_extras_data = {
            'id': 456,
            'email': 'extra@example.com',
            'created_at': 1640995200,
            'extra_field': 'extra_value',
        }
        member_with_extras = Member.model_validate(member_with_extras_data)

        # Should contain the extra data
        assert member_with_extras.extras == {'extra_field': 'extra_value'}

        # Verify it's read-only (no setter method)
        assert not hasattr(Member.extras, 'fset') or Member.extras.fset is None
