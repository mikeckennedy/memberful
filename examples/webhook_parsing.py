"""Example of parsing Memberful webhooks with Pydantic models."""

import json
from typing import Union

from memberful.models import (
    WebhookEvent,
    MemberSignupEvent,
    SubscriptionCreatedEvent,
    OrderCompletedEvent,
    SubscriptionPlanCreatedEvent,
    DownloadCreatedEvent,
)


def parse_webhook_payload(payload: str) -> WebhookEvent:
    """Parse a webhook payload into the appropriate Pydantic model.
    
    Args:
        payload: Raw JSON webhook payload
        
    Returns:
        Parsed webhook event model
        
    Raises:
        ValueError: If the payload format is invalid
    """
    try:
        data = json.loads(payload)
        event_type = data.get('event')
        
        # Parse based on event type
        if event_type == 'member_signup':
            return MemberSignupEvent(**data)
        elif event_type == 'subscription.created':
            return SubscriptionCreatedEvent(**data)
        elif event_type == 'order.completed':
            return OrderCompletedEvent(**data)
        elif event_type == 'subscription_plan.created':
            return SubscriptionPlanCreatedEvent(**data)
        elif event_type == 'download.created':
            return DownloadCreatedEvent(**data)
        else:
            # For other event types, you can add more specific parsing
            # or use a generic approach with Pydantic's discriminated unions
            raise ValueError(f'Unsupported event type: {event_type}')
            
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise ValueError(f'Invalid webhook payload: {e}')


def handle_webhook_event(event: WebhookEvent):
    """Handle different webhook event types.
    
    Args:
        event: Parsed webhook event
    """
    if isinstance(event, MemberSignupEvent):
        print(f'🎉 New member signed up: {event.member.email}')
        if event.member.first_name:
            print(f'   Welcome, {event.member.first_name}!')
        if event.member.tracking_params:
            print(f'   Came from: {event.member.tracking_params.utm_source}')
            
    elif isinstance(event, SubscriptionCreatedEvent):
        print(f'💳 New subscription created for: {event.member.email}')
        for sub in event.subscriptions:
            plan = sub.subscription
            print(f'   Plan: {plan.name} (${plan.price/100:.2f})')
            
    elif isinstance(event, OrderCompletedEvent):
        print(f'✅ Order completed: {event.order.number}')
        print(f'   Total: ${event.order.total/100:.2f}')
        print(f'   Member: {event.order.member.email}')
        
    elif isinstance(event, SubscriptionPlanCreatedEvent):
        plan = event.subscription
        print(f'📋 New subscription plan created: {plan.name}')
        print(f'   Price: ${plan.price/100:.2f}/{plan.renewal_period}')
        
    elif isinstance(event, DownloadCreatedEvent):
        product = event.product
        print(f'📦 New download created: {product.name}')
        print(f'   Price: ${product.price/100:.2f}')
        
    else:
        print(f'📨 Received webhook: {event.event}')


def main():
    """Example usage of webhook parsing."""
    
    # Example 1: Member signup
    member_signup_json = '''
    {
      "event": "member_signup",
      "member": {
        "id": 12345,
        "email": "jane.doe@example.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "created_at": 1640995200,
        "signup_method": "checkout",
        "tracking_params": {
          "utm_source": "twitter",
          "utm_campaign": "winter_sale"
        },
        "unrestricted_access": false
      }
    }
    '''
    
    try:
        event = parse_webhook_payload(member_signup_json)
        handle_webhook_event(event)
        print()
        
        # Access typed data safely
        if isinstance(event, MemberSignupEvent):
            member = event.member
            print(f'Member details:')
            print(f'  ID: {member.id}')
            print(f'  Name: {member.first_name} {member.last_name}')
            print(f'  Email: {member.email}')
            print(f'  Signup method: {member.signup_method}')
            if member.tracking_params:
                print(f'  UTM Source: {member.tracking_params.utm_source}')
                print(f'  UTM Campaign: {member.tracking_params.utm_campaign}')
        print()
        
    except ValueError as e:
        print(f'❌ Error parsing webhook: {e}')
    
    # Example 2: Subscription plan created
    plan_created_json = '''
    {
      "event": "subscription_plan.created",
      "subscription": {
        "id": 42,
        "price": 2999,
        "name": "Premium Plan",
        "slug": "premium-plan",
        "renewal_period": "monthly",
        "interval_unit": "month",
        "interval_count": 1,
        "for_sale": true
      }
    }
    '''
    
    try:
        event = parse_webhook_payload(plan_created_json)
        handle_webhook_event(event)
        
        # Access plan details with full type safety
        if isinstance(event, SubscriptionPlanCreatedEvent):
            plan = event.subscription
            print(f'Plan details:')
            print(f'  ID: {plan.id}')
            print(f'  Name: {plan.name}')
            print(f'  Price: ${plan.price/100:.2f}')
            print(f'  Renewal: {plan.renewal_period}')
            print(f'  For sale: {plan.for_sale}')
        
    except ValueError as e:
        print(f'❌ Error parsing webhook: {e}')


if __name__ == '__main__':
    print('🔗 Memberful Webhook Parsing Examples')
    print('=====================================\\n')
    main()
