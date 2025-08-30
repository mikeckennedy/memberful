"""FastAPI example app for handling Memberful webhooks.

This example demonstrates how to create a FastAPI webhook endpoint
that can handle all Memberful webhook event types using the
existing webhook models and parsing functionality.
"""

import json
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, status

# Import the webhook models and parsing function from the memberful package
from memberful.webhooks import (
    DownloadCreatedEvent,
    DownloadDeletedEvent,
    DownloadUpdatedEvent,
    MemberSignupEvent,
    MemberUpdatedEvent,
    OrderCompletedEvent,
    OrderSuspendedEvent,
    SubscriptionCreatedEvent,
    SubscriptionPlanCreatedEvent,
    SubscriptionPlanDeletedEvent,
    SubscriptionPlanUpdatedEvent,
    SubscriptionUpdatedEvent,
    WebhookEvent,
    parse_payload,
)

app = FastAPI(
    title='Memberful Webhook Handler',
    description='A FastAPI app that handles all Memberful webhook events',
    version='1.0.0',
)


def handle_member_signup(event: MemberSignupEvent):
    """Handle member signup webhook events."""
    print(f'🎉 [MEMBER SIGNUP] New member signed up: {event.member.email}')
    if event.member.first_name:
        print(f'   Welcome, {event.member.first_name}!')
    if event.member.tracking_params and event.member.tracking_params.utm_source:
        print(f'   Came from: {event.member.tracking_params.utm_source}')
    print(f'   Member ID: {event.member.id}')
    print(f'   Signup method: {event.member.signup_method}')


def handle_member_updated(event: MemberUpdatedEvent):
    """Handle member updated webhook events."""
    print(f'👤 [MEMBER UPDATED] Member updated: {event.member.email}')
    print(f'   Member ID: {event.member.id}')
    print(f'   Active subscriptions: {len(event.subscriptions)}')
    print(f'   Access to products: {len(event.products)}')


def handle_subscription_created(event: SubscriptionCreatedEvent):
    """Handle subscription created webhook events."""
    print(f'💳 [SUBSCRIPTION CREATED] New subscription for: {event.member.email}')
    for sub in event.subscriptions:
        plan = sub.subscription
        print(f'   Plan: {plan.name} (${plan.price / 100:.2f})')
        print(f'   Renewal: {plan.renewal_period}')
        print(f'   Active: {sub.active}')


def handle_subscription_updated(event: SubscriptionUpdatedEvent):
    """Handle subscription updated webhook events."""
    print(f'🔄 [SUBSCRIPTION UPDATED] Subscription updated for: {event.member.email}')
    for sub in event.subscriptions:
        plan = sub.subscription
        print(f'   Plan: {plan.name} (${plan.price / 100:.2f})')
        print(f'   Active: {sub.active}')
    if event.changed:
        print(f'   Changes detected: {event.changed}')


def handle_order_completed(event: OrderCompletedEvent):
    """Handle order completed webhook events."""
    print(f'✅ [ORDER COMPLETED] Order completed: {event.order.number}')
    print(f'   Total: ${event.order.total / 100:.2f}')
    print(f'   Member: {event.order.member.email}')
    print(f'   Status: {event.order.status}')
    print(f'   Products: {len(event.order.products)}')


def handle_order_suspended(event: OrderSuspendedEvent):
    """Handle order suspended webhook events."""
    print(f'⏸️  [ORDER SUSPENDED] Order suspended: {event.order.number}')
    print(f'   Total: ${event.order.total / 100:.2f}')
    print(f'   Member: {event.order.member.email}')
    print(f'   Status: {event.order.status}')


def handle_subscription_plan_created(event: SubscriptionPlanCreatedEvent):
    """Handle subscription plan created webhook events."""
    plan = event.subscription
    print(f'📋 [PLAN CREATED] New subscription plan: {plan.name}')
    print(f'   Price: ${plan.price / 100:.2f}/{plan.renewal_period}')
    print(f'   Slug: {plan.slug}')
    print(f'   For sale: {plan.for_sale}')


def handle_subscription_plan_updated(event: SubscriptionPlanUpdatedEvent):
    """Handle subscription plan updated webhook events."""
    plan = event.subscription
    print(f'📝 [PLAN UPDATED] Subscription plan updated: {plan.name}')
    print(f'   Price: ${plan.price / 100:.2f}/{plan.renewal_period}')
    print(f'   Slug: {plan.slug}')
    print(f'   For sale: {plan.for_sale}')


def handle_subscription_plan_deleted(event: SubscriptionPlanDeletedEvent):
    """Handle subscription plan deleted webhook events."""
    plan = event.subscription
    print(f'🗑️  [PLAN DELETED] Subscription plan deleted: {plan.name}')
    print(f'   Former price: ${plan.price / 100:.2f}/{plan.renewal_period}')
    print(f'   Slug: {plan.slug}')


def handle_download_created(event: DownloadCreatedEvent):
    """Handle download created webhook events."""
    product = event.product
    print(f'📦 [DOWNLOAD CREATED] New download created: {product.name}')
    print(f'   Price: ${product.price / 100:.2f}')
    print(f'   Product ID: {product.id}')
    print(f'   Slug: {product.slug}')


def handle_download_updated(event: DownloadUpdatedEvent):
    """Handle download updated webhook events."""
    product = event.product
    print(f'📝 [DOWNLOAD UPDATED] Download updated: {product.name}')
    print(f'   Price: ${product.price / 100:.2f}')
    print(f'   Product ID: {product.id}')
    print(f'   For sale: {product.for_sale}')


def handle_download_deleted(event: DownloadDeletedEvent):
    """Handle download deleted webhook events."""
    product = event.product
    print(f'🗑️  [DOWNLOAD DELETED] Download deleted: {product.name}')
    print(f'   Former price: ${product.price / 100:.2f}')
    print(f'   Product ID: {product.id}')


def handle_webhook_event(event: WebhookEvent):
    """Route webhook events to the appropriate handler function."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'\n[{timestamp}] Processing webhook event: {event.event}')
    print('-' * 60)

    # Handle different event types using match statement
    match event:
        case MemberSignupEvent():
            handle_member_signup(event)
        case MemberUpdatedEvent():
            handle_member_updated(event)
        case SubscriptionCreatedEvent():
            handle_subscription_created(event)
        case SubscriptionUpdatedEvent():
            handle_subscription_updated(event)
        case OrderCompletedEvent():
            handle_order_completed(event)
        case OrderSuspendedEvent():
            handle_order_suspended(event)
        case SubscriptionPlanCreatedEvent():
            handle_subscription_plan_created(event)
        case SubscriptionPlanUpdatedEvent():
            handle_subscription_plan_updated(event)
        case SubscriptionPlanDeletedEvent():
            handle_subscription_plan_deleted(event)
        case DownloadCreatedEvent():
            handle_download_created(event)
        case DownloadUpdatedEvent():
            handle_download_updated(event)
        case DownloadDeletedEvent():
            handle_download_deleted(event)
        case _:  # type: ignore # noqa: PERF102
            print(f'📨 [UNKNOWN EVENT] Received webhook: {event.event}')

    print('-' * 60)


@app.get('/')
async def root():
    """Root endpoint with basic app information."""
    return {
        'message': 'Memberful Webhook Handler API',
        'version': '1.0.0',
        'endpoints': {'webhook': '/webhook', 'health': '/health'},
    }


@app.get('/health')
async def health_check():
    """Health check endpoint."""
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}


@app.post('/webhook')
async def webhook_endpoint(request: Request):
    """Main webhook endpoint that handles all Memberful webhook events.

    This endpoint accepts webhook payloads from Memberful and routes them
    to the appropriate handler based on the event type.
    """
    try:
        # Get the raw request body
        raw_body = await request.body()

        # Parse JSON payload
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError as e:
            print(f'❌ Failed to parse JSON: {e}')
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid JSON payload')

        # Parse the webhook event using our models
        try:
            webhook_event = parse_payload(payload)
            handle_webhook_event(webhook_event)

            return {'status': 'success', 'event_type': webhook_event.event, 'message': 'Webhook processed successfully'}

        except ValueError as e:
            print(f'❌ Failed to parse webhook event: {e}')
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Invalid webhook payload: {str(e)}')

    except Exception as e:
        print(f'❌ Unexpected error processing webhook: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error')


if __name__ == '__main__':
    import uvicorn

    print('🚀 Starting Memberful Webhook Handler API...')
    print('📡 Webhook endpoint: http://localhost:8000/webhook')
    print('🏥 Health check: http://localhost:8000/health')
    print('📚 API docs: http://localhost:8000/docs')
    print('\n💡 Send webhook payloads to /webhook to see them handled!')

    uvicorn.run(app, host='0.0.0.0', port=8000)
