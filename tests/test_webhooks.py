"""Tests for webhook handling functionality."""

from typing import Any

from memberful.webhooks import (
    MemberDeletedEvent,
    MemberSignupEvent,
    SubscriptionActivatedEvent,
    SubscriptionDeletedEvent,
    SubscriptionRenewedEvent,
    parse_payload,
    validate_signature,
)


class TestWebhookFunctions:
    """Test cases for webhook functions."""

    def test_parse_webhook_payload_member_signup(self):
        """Test parsing a member signup webhook payload."""
        payload = {
            'event': 'member_signup',
            'member': {
                'id': 12345,
                'email': 'test@example.com',
                'full_name': 'Test User',
                'created_at': 1640995200,  # Unix timestamp for Jan 1, 2022
            },
        }

        event = parse_payload(payload)
        assert isinstance(event, MemberSignupEvent)
        assert event.member.id == 12345
        assert event.member.email == 'test@example.com'

    def test_parse_webhook_payload_unsupported_event(self):
        """Test that unsupported event types raise ValueError."""
        payload: dict[str, Any] = {'event': 'unsupported_event', 'data': {}}

        try:
            parse_payload(payload)
            assert False, 'Should have raised ValueError'
        except ValueError as e:
            assert 'Unsupported event type' in str(e)

    def test_validate_webhook_signature_valid(self):
        """Test webhook signature validation with valid signature."""
        payload = '{"event":"member_signup","member":{"id":123}}'
        secret_key = 'test_secret'

        # Generate expected signature
        import hashlib
        import hmac

        expected_sig = hmac.new(secret_key.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()

        # Test without sha256= prefix
        assert validate_signature(payload, expected_sig, secret_key) is True

        # Test with sha256= prefix
        assert validate_signature(payload, f'sha256={expected_sig}', secret_key) is True

    def test_validate_webhook_signature_invalid(self):
        """Test webhook signature validation with invalid signature."""
        payload = '{"event":"member_signup"}'
        secret_key = 'test_secret'
        invalid_signature = 'invalid_signature'

        assert validate_signature(payload, invalid_signature, secret_key) is False

    def test_parse_webhook_payload_member_deleted(self):
        """Test parsing a member deleted webhook payload."""
        payload = {
            'event': 'member.deleted',
            'member': {
                'id': 12345,
                'deleted': True,
            },
            'products': [],
            'subscriptions': [],
        }

        event = parse_payload(payload)
        assert isinstance(event, MemberDeletedEvent)
        assert event.member.id == 12345
        assert event.member.deleted is True

    def test_parse_webhook_payload_subscription_activated(self):
        """Test parsing a subscription activated webhook payload."""
        payload = {
            'event': 'subscription.activated',
            'products': [],
            'subscriptions': [
                {
                    'active': True,
                    'created_at': 1640995200,
                    'expires': True,
                    'expires_at': 1672531200,
                    'id': 67890,
                    'subscription': {
                        'id': 1,
                        'price': 999,
                        'name': 'Premium Plan',
                        'slug': 'premium',
                        'renewal_period': 'monthly',
                        'interval_unit': 'month',
                        'interval_count': 1,
                    },
                }
            ],
        }

        event = parse_payload(payload)
        assert isinstance(event, SubscriptionActivatedEvent)
        assert event.member is None  # No member data in subscription events
        assert len(event.subscriptions) == 1
        assert event.subscriptions[0].active is True

    def test_parse_webhook_payload_subscription_deleted(self):
        """Test parsing a subscription deleted webhook payload."""
        payload = {
            'event': 'subscription.deleted',
            'products': [],
            'subscriptions': [],
        }

        event = parse_payload(payload)
        assert isinstance(event, SubscriptionDeletedEvent)
        assert event.member is None  # No member data in subscription events

    def test_parse_webhook_payload_subscription_renewed(self):
        """Test parsing a subscription renewed webhook payload."""
        payload = {
            'event': 'subscription.renewed',
            'products': [],
            'subscriptions': [
                {
                    'active': True,
                    'created_at': 1640995200,
                    'expires': True,
                    'expires_at': 1675123200,  # Renewed expiration date
                    'id': 67890,
                    'subscription': {
                        'id': 1,
                        'price': 999,
                        'name': 'Premium Plan',
                        'slug': 'premium',
                        'renewal_period': 'monthly',
                        'interval_unit': 'month',
                        'interval_count': 1,
                    },
                }
            ],
        }

        event = parse_payload(payload)
        assert isinstance(event, SubscriptionRenewedEvent)
        assert event.member is None  # No member data in subscription events
        assert len(event.subscriptions) == 1
        assert event.subscriptions[0].expires_at == 1675123200
