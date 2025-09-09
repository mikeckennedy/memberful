"""Basic webhook usage examples for the memberful package."""

import json

from memberful.webhooks import (
    MemberDeletedEvent,
    MemberSignupEvent,
    SubscriptionActivatedEvent,
    SubscriptionCreatedEvent,
    SubscriptionDeletedEvent,
    SubscriptionRenewedEvent,
    parse_payload,
    validate_signature,
)


def handle_member_signup(event: MemberSignupEvent):
    """Handle new member signup events."""
    print(f'New member signed up: {event.member.email}')
    # Add your custom logic here


def handle_subscription_created(event: SubscriptionCreatedEvent):
    """Handle subscription created events."""
    print(f'New subscription created for member: {event.member.id}')
    # Add your custom logic here


def handle_member_deleted(event: MemberDeletedEvent):
    """Handle member deleted events."""
    print(f'Member deleted: {event.member.email} (ID: {event.member.id})')
    # Add your custom logic here (cleanup, analytics, etc.)


def handle_subscription_activated(event: SubscriptionActivatedEvent):
    """Handle subscription activated events."""
    print(f'Subscription activated for member: {event.member.email}')
    # Add your custom logic here (send welcome email, grant access, etc.)


def handle_subscription_deleted(event: SubscriptionDeletedEvent):
    """Handle subscription deleted events."""
    print(f'Subscription deleted for member: {event.member.email}')
    # Add your custom logic here (revoke access, send notification, etc.)


def handle_subscription_renewed(event: SubscriptionRenewedEvent):
    """Handle subscription renewed events."""
    print(f'Subscription renewed for member: {event.member.email}')
    # Add your custom logic here (update billing, send receipt, etc.)


def process_webhook(payload: str, signature: str, secret_key: str):
    """Process an incoming webhook payload."""
    # 1. Validate the signature
    if not validate_signature(payload, signature, secret_key):
        raise ValueError('Invalid webhook signature')

    # 2. Parse the payload into a strongly-typed event
    event_data = json.loads(payload)
    webhook_event = parse_payload(event_data)

    # 3. Route to appropriate handler using match statement
    match webhook_event:
        case MemberSignupEvent():
            handle_member_signup(webhook_event)
        case MemberDeletedEvent():
            handle_member_deleted(webhook_event)
        case SubscriptionCreatedEvent():
            handle_subscription_created(webhook_event)
        case SubscriptionActivatedEvent():
            handle_subscription_activated(webhook_event)
        case SubscriptionDeletedEvent():
            handle_subscription_deleted(webhook_event)
        case SubscriptionRenewedEvent():
            handle_subscription_renewed(webhook_event)
        case _:
            print(f'Unhandled event type: {webhook_event.event}')

    return webhook_event


def webhook_example():
    """Example webhook handling setup using the functional approach."""
    # In your web framework (Flask, FastAPI, etc.), process webhooks like this:

    # Example usage:
    # payload = request.get_data(as_text=True)
    # signature = request.headers.get('X-Memberful-Webhook-Signature')
    # event = process_webhook(payload, signature, 'your_webhook_secret_key')
    # print(f"Processed webhook event: {event.event}")

    print('Webhook processing example setup complete!')


if __name__ == '__main__':
    print('Running Memberful webhook examples...')

    # Show webhook handler setup
    webhook_example()

    print('Webhook examples completed!')
