"""Comprehensive webhook usage examples for the memberful package.

This example demonstrates how to handle all available Memberful webhook events
using the memberful package's type-safe webhook models. Each event type has
a dedicated handler function that shows how to access the event data and
suggests common use cases.

Webhook Events Covered:
- Member events: signup, updated, deleted
- Subscription events: created, updated, activated, deactivated, deleted, renewed
- Order events: purchased, refunded, completed, suspended
- Subscription plan events: created, updated, deleted
- Download/product events: created, updated, deleted

Usage:
    1. Set up your webhook endpoint in your web framework
    2. Use validate_signature() to verify webhook authenticity
    3. Use parse_payload() to get strongly-typed event objects
    4. Route events to appropriate handlers using pattern matching
"""

import json

from memberful.webhooks import (
    DownloadCreatedEvent,
    DownloadDeletedEvent,
    DownloadUpdatedEvent,
    MemberDeletedEvent,
    MemberSignupEvent,
    MemberUpdatedEvent,
    OrderCompletedEvent,
    OrderPurchasedEvent,
    OrderRefundedEvent,
    OrderSuspendedEvent,
    SubscriptionActivatedEvent,
    SubscriptionCreatedEvent,
    SubscriptionDeactivatedEvent,
    SubscriptionDeletedEvent,
    SubscriptionPlanCreatedEvent,
    SubscriptionPlanDeletedEvent,
    SubscriptionPlanUpdatedEvent,
    SubscriptionRenewedEvent,
    SubscriptionUpdatedEvent,
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
    print(f'Member deleted: ID {event.member.id} (deleted: {event.member.deleted})')
    # Note: Only member ID and deleted flag are available, full member data is not included
    # Add your custom logic here (cleanup, analytics, etc.)


def handle_subscription_activated(event: SubscriptionActivatedEvent):
    """Handle subscription activated events."""
    print(f'Subscription activated: {event.subscription.id} for member {event.subscription.member.email}')
    print(f'Plan: {event.subscription.subscription_plan.name}')
    # Add your custom logic here (send welcome email, grant access, etc.)


def handle_subscription_deleted(event: SubscriptionDeletedEvent):
    """Handle subscription deleted events."""
    print(f'Subscription deleted: {event.subscription.id} for member {event.subscription.member.email}')
    print(f'Plan: {event.subscription.subscription_plan.name}')
    # Add your custom logic here (revoke access, send notification, etc.)


def handle_subscription_renewed(event: SubscriptionRenewedEvent):
    """Handle subscription renewed events."""
    print(f'Subscription renewed: {event.subscription.id} for member {event.subscription.member.email}')
    print(f'Order: {event.order.uuid} - Total: ${event.order.total / 100:.2f}')
    # Add your custom logic here (update billing, send receipt, etc.)


def handle_member_updated(event: MemberUpdatedEvent):
    """Handle member profile updated events."""
    print(f'Member updated: {event.member.email} (ID: {event.member.id})')
    if event.changed:
        print(f'Changed fields: {list(event.changed.model_dump(exclude_none=True).keys())}')
    # Add your custom logic here (sync profile data, update permissions, etc.)


def handle_subscription_updated(event: SubscriptionUpdatedEvent):
    """Handle subscription updated events."""
    print(f'Subscription updated: {event.subscription.id} for member {event.subscription.member.email}')
    if event.changed:
        changes = event.changed.model_dump(exclude_none=True)
        print(f'Changed fields: {list(changes.keys())}')
        # Check for plan changes
        if event.changed.plan_id:
            old_plan, new_plan = event.changed.plan_id
            print(f'Plan changed from {old_plan} to {new_plan}')
    # Add your custom logic here (update access levels, billing changes, etc.)


def handle_subscription_deactivated(event: SubscriptionDeactivatedEvent):
    """Handle subscription deactivated events."""
    print(f'Subscription deactivated: {event.subscription.id} for member {event.subscription.member.email}')
    print(f'Subscription expires at: {event.subscription.expires_at}')
    # Add your custom logic here (revoke access, send expiration notice, etc.)


def handle_order_purchased(event: OrderPurchasedEvent):
    """Handle order purchased events."""
    print(f'Order purchased: {event.order.uuid} - Total: ${event.order.total / 100:.2f}')
    if event.order.member:
        print(f'Customer: {event.order.member.email}')
    print(f'Products: {len(event.order.products)} item(s)')
    # Add your custom logic here (send confirmation, fulfill order, etc.)


def handle_order_refunded(event: OrderRefundedEvent):
    """Handle order refunded events."""
    print(f'Order refunded: {event.order.uuid} - Amount: ${event.order.total / 100:.2f}')
    if event.order.member:
        print(f'Customer: {event.order.member.email}')
    # Add your custom logic here (process refund, update inventory, etc.)


def handle_order_completed(event: OrderCompletedEvent):
    """Handle order completed events."""
    print(f'Order completed: {event.order.uuid} - Total: ${event.order.total / 100:.2f}')
    if event.order.member:
        print(f'Customer: {event.order.member.email}')
    # Add your custom logic here (activate services, send welcome email, etc.)


def handle_order_suspended(event: OrderSuspendedEvent):
    """Handle order suspended events."""
    print(f'Order suspended: {event.order.uuid} - Total: ${event.order.total / 100:.2f}')
    if event.order.member:
        print(f'Customer: {event.order.member.email}')
    # Add your custom logic here (suspend services, send notification, etc.)


def handle_subscription_plan_created(event: SubscriptionPlanCreatedEvent):
    """Handle subscription plan created events."""
    print(f'New subscription plan created: {event.subscription.name} (ID: {event.subscription.id})')
    print(f'Price: ${(event.subscription.price or 0) / 100:.2f} per {event.subscription.renewal_period}')
    # Add your custom logic here (update pricing displays, sync with external systems, etc.)


def handle_subscription_plan_updated(event: SubscriptionPlanUpdatedEvent):
    """Handle subscription plan updated events."""
    print(f'Subscription plan updated: {event.subscription.name} (ID: {event.subscription.id})')
    print(f'Price: ${(event.subscription.price or 0) / 100:.2f} per {event.subscription.renewal_period}')
    # Add your custom logic here (update pricing displays, notify existing subscribers, etc.)


def handle_subscription_plan_deleted(event: SubscriptionPlanDeletedEvent):
    """Handle subscription plan deleted events."""
    print(f'Subscription plan deleted: {event.subscription.name} (ID: {event.subscription.id})')
    # Add your custom logic here (remove from displays, handle existing subscribers, etc.)


def handle_download_created(event: DownloadCreatedEvent):
    """Handle download/product created events."""
    print(f'New download created: {event.product.name} (ID: {event.product.id})')
    print(f'Price: ${event.product.price / 100:.2f}')
    # Add your custom logic here (update product catalogs, sync inventory, etc.)


def handle_download_updated(event: DownloadUpdatedEvent):
    """Handle download/product updated events."""
    print(f'Download updated: {event.product.name} (ID: {event.product.id})')
    print(f'Price: ${event.product.price / 100:.2f}')
    # Add your custom logic here (update product displays, sync changes, etc.)


def handle_download_deleted(event: DownloadDeletedEvent):
    """Handle download/product deleted events."""
    print(f'Download deleted: {event.product.name} (ID: {event.product.id})')
    # Add your custom logic here (remove from catalogs, handle existing purchases, etc.)


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
        # Member events
        case MemberSignupEvent():
            handle_member_signup(webhook_event)
        case MemberUpdatedEvent():
            handle_member_updated(webhook_event)
        case MemberDeletedEvent():
            handle_member_deleted(webhook_event)
        
        # Subscription events
        case SubscriptionCreatedEvent():
            handle_subscription_created(webhook_event)
        case SubscriptionUpdatedEvent():
            handle_subscription_updated(webhook_event)
        case SubscriptionActivatedEvent():
            handle_subscription_activated(webhook_event)
        case SubscriptionDeactivatedEvent():
            handle_subscription_deactivated(webhook_event)
        case SubscriptionDeletedEvent():
            handle_subscription_deleted(webhook_event)
        case SubscriptionRenewedEvent():
            handle_subscription_renewed(webhook_event)
        
        # Order events
        case OrderPurchasedEvent():
            handle_order_purchased(webhook_event)
        case OrderRefundedEvent():
            handle_order_refunded(webhook_event)
        case OrderCompletedEvent():
            handle_order_completed(webhook_event)
        case OrderSuspendedEvent():
            handle_order_suspended(webhook_event)
        
        # Subscription plan events
        case SubscriptionPlanCreatedEvent():
            handle_subscription_plan_created(webhook_event)
        case SubscriptionPlanUpdatedEvent():
            handle_subscription_plan_updated(webhook_event)
        case SubscriptionPlanDeletedEvent():
            handle_subscription_plan_deleted(webhook_event)
        
        # Download/Product events
        case DownloadCreatedEvent():
            handle_download_created(webhook_event)
        case DownloadUpdatedEvent():
            handle_download_updated(webhook_event)
        case DownloadDeletedEvent():
            handle_download_deleted(webhook_event)
        
        case _:
            print(f'Unhandled event type: {webhook_event.event}')

    return webhook_event


def webhook_example():
    """Example webhook handling setup using the functional approach.
    
    This function demonstrates the typical flow for processing Memberful webhooks
    in a web application. The pattern shown here can be adapted to any web
    framework (Flask, FastAPI, Django, etc.).
    
    Key steps:
    1. Extract raw payload and signature from the HTTP request
    2. Validate the webhook signature for security
    3. Parse the payload into a strongly-typed event object
    4. Route the event to the appropriate handler function
    
    Security Note:
    Always validate webhook signatures in production to ensure the webhook
    is actually from Memberful and hasn't been tampered with.
    """
    # In your web framework (Flask, FastAPI, etc.), process webhooks like this:

    # Example usage:
    # payload = request.get_data(as_text=True)  # Raw request body as string
    # signature = request.headers.get('X-Memberful-Webhook-Signature')
    # secret_key = 'your_webhook_secret_key'  # From Memberful dashboard
    # 
    # try:
    #     event = process_webhook(payload, signature, secret_key)
    #     print(f"Successfully processed webhook event: {event.event}")
    #     return {'status': 'success'}, 200
    # except ValueError as e:
    #     print(f"Webhook processing failed: {e}")
    #     return {'error': str(e)}, 400

    print('Comprehensive webhook processing example setup complete!')
    print('This example now handles all 17 Memberful webhook event types!')


if __name__ == '__main__':
    print('Running comprehensive Memberful webhook examples...')
    print('\nThis example demonstrates handlers for all webhook event types:')
    print('- Member events: signup, updated, deleted')
    print('- Subscription events: created, updated, activated, deactivated, deleted, renewed')
    print('- Order events: purchased, refunded, completed, suspended')
    print('- Subscription plan events: created, updated, deleted')
    print('- Download/product events: created, updated, deleted')
    print()

    # Show webhook handler setup
    webhook_example()

    print('\nWebhook examples completed!')
    print('Ready to handle all Memberful webhook events with type safety!')
