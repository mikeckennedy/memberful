# Memberful Webhook Events Reference

This document contains the JSON structures for all Memberful webhook events as documented at [Memberful Webhook Event Reference](https://memberful.com/help/custom-development-and-api/webhook-event-reference/).

## Pydantic Models

Each webhook event has a corresponding Pydantic model in `src/memberful/webhooks/models.py` for type-safe parsing and validation. Import these models from:

```python
from memberful.webhooks import (
    MemberSignupEvent,
    MemberUpdatedEvent,
    MemberDeletedEvent,
    DeletedMember,  # Special model for deleted member events
    SubscriptionCreatedEvent,
    SubscriptionUpdatedEvent,
    SubscriptionActivatedEvent,
    SubscriptionDeletedEvent,
    SubscriptionRenewedEvent,
    OrderCompletedEvent,
    OrderSuspendedEvent,
    SubscriptionPlanCreatedEvent,
    SubscriptionPlanUpdatedEvent,
    SubscriptionPlanDeletedEvent,
    DownloadCreatedEvent,
    DownloadUpdatedEvent,
    DownloadDeletedEvent,
    WebhookEvent,  # Union of all event types
)
```

## Member Events

### member_signup
Triggered when a new member account is created.

**Pydantic Model:** `MemberSignupEvent`

```json
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
      "exp_year": 2040,
      "last_four": "4242",
      "brand": "visa"
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
```

### member_updated  
Triggered when a member is updated.

**Pydantic Model:** `MemberUpdatedEvent`

```json
{
  "event": "member_updated",
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
      "exp_year": 2040,
      "last_four": "4242",
      "brand": "visa"
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
  },
  "products": [],
  "subscriptions": [
    {
      "active": true,
      "created_at": 1756245496,
      "expires": true,
      "expires_at": 1758837496,
      "id": 0,
      "in_trial_period": false,
      "subscription": {
        "id": 0,
        "price": 1000,
        "name": "Sample plan",
        "slug": "0-sample-plan",
        "renewal_period": "monthly",
        "interval_unit": "month", 
        "interval_count": 1,
        "for_sale": true,
        "type": "standard_plan"
      },
      "trial_end_at": null,
      "trial_start_at": null
    }
  ]
}
```

### member.deleted
Triggered when a member account is deleted.

**Pydantic Model:** `MemberDeletedEvent`

**Note:** When a member is deleted, Memberful only sends minimal member information (just the ID and deleted flag), as the full member data is no longer available.

```json
{
  "event": "member.deleted",
  "member": {
    "id": 12345,
    "deleted": true
  },
  "products": [],
  "subscriptions": []
}
```

## Subscription Events

### subscription.created
Triggered when a new subscription is created.

**Pydantic Model:** `SubscriptionCreatedEvent`

**Note:** Subscription events do not include member data in the payload, only subscription-related information.

```json
{
  "event": "subscription.created",
  "products": [],
  "subscriptions": [
    {
      "active": true, 
      "created_at": 1756245496,
      "expires": true,
      "expires_at": 1758837496,
      "id": 0,
      "in_trial_period": false,
      "subscription": {
        "id": 0,
        "price": 1000,
        "name": "Sample plan",
        "slug": "0-sample-plan",
        "renewal_period": "monthly",
        "interval_unit": "month",
        "interval_count": 1,
        "for_sale": true
      },
      "trial_end_at": null,
      "trial_start_at": null
    }
  ]
}
```

### subscription.updated
Triggered when a subscription is updated (including upgrades and downgrades).

**Pydantic Model:** `SubscriptionUpdatedEvent`

**Note:** Subscription events do not include member data in the payload, only subscription-related information.

```json
{
  "event": "subscription.updated",
  "products": [],
  "subscriptions": [
    {
      "active": true,
      "created_at": 1756245496,
      "expires": true,
      "expires_at": 1758837496,
      "id": 0,
      "in_trial_period": false,
      "subscription": {
        "id": 0,
        "price": 1000,
        "name": "Sample plan",
        "slug": "0-sample-plan",
        "renewal_period": "monthly",
        "interval_unit": "month",
        "interval_count": 1,
        "for_sale": true
      },
      "trial_end_at": null,
      "trial_start_at": null
    }
  ],
  "changed": {
    "plan_id": [42, 0],
    "expires_at": ["2023-05-12T15:09:58Z", "2023-06-11T15:09:58Z"],
    "autorenew": [false, true]
  }
}
```

### subscription.activated
Triggered when a subscription is activated.

**Pydantic Model:** `SubscriptionActivatedEvent`

**Note:** Subscription events do not include member data in the payload, only subscription-related information.

```json
{
  "event": "subscription.activated",
  "products": [],
  "subscriptions": [
    {
      "active": true,
      "created_at": 1756245496,
      "expires": true,
      "expires_at": 1758837496,
      "id": 0,
      "in_trial_period": false,
      "subscription": {
        "id": 0,
        "price": 1000,
        "name": "Sample plan",
        "slug": "0-sample-plan",
        "renewal_period": "monthly",
        "interval_unit": "month",
        "interval_count": 1,
        "for_sale": true
      },
      "trial_end_at": null,
      "trial_start_at": null
    }
  ]
}
```

### subscription.deleted
Triggered when a subscription is deleted.

**Pydantic Model:** `SubscriptionDeletedEvent`

**Note:** Subscription events do not include member data in the payload, only subscription-related information.

```json
{
  "event": "subscription.deleted",
  "products": [],
  "subscriptions": []
}
```

### subscription.renewed
Triggered when a subscription is renewed.

**Pydantic Model:** `SubscriptionRenewedEvent`

**Note:** Subscription events do not include member data in the payload, only subscription-related information.

```json
{
  "event": "subscription.renewed",
  "products": [],
  "subscriptions": [
    {
      "active": true,
      "created_at": 1756245496,
      "expires": true,
      "expires_at": 1761421496,
      "id": 0,
      "in_trial_period": false,
      "subscription": {
        "id": 0,
        "price": 1000,
        "name": "Sample plan",
        "slug": "0-sample-plan",
        "renewal_period": "monthly",
        "interval_unit": "month",
        "interval_count": 1,
        "for_sale": true
      },
      "trial_end_at": null,
      "trial_start_at": null
    }
  ]
}
```

## Order Events

### order.completed
Triggered when a suspended order is marked completed by staff.

**Pydantic Model:** `OrderCompletedEvent`

```json
{
  "event": "order.completed",
  "order": {
    "uuid": "4DACB7B0-B728-0130-F9E8-102B343DC979",
    "number": "4DACB7B0",
    "total": 9900,
    "status": "completed", 
    "receipt": "receipt text",
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
    },
    "products": [],
    "subscriptions": [
      {
        "active": true,
        "created_at": 1756245496,
        "expires": true,
        "expires_at": 1758837496,
        "id": 0,
        "in_trial_period": false,
        "subscription": {
          "id": 0,
          "price": 1000,
          "name": "Sample plan",
          "slug": "0-sample-plan",
          "renewal_period": "monthly",
          "interval_unit": "month",
          "interval_count": 1,
          "for_sale": true
        },
        "trial_end_at": null,
        "trial_start_at": null
      }
    ]
  }
}
```

### order.suspended  
Triggered when an order is suspended by staff.

**Pydantic Model:** `OrderSuspendedEvent`

```json
{
  "event": "order.suspended",
  "order": {
    "uuid": "4DACB7B0-B728-0130-F9E8-102B343DC979",
    "number": "4DACB7B0", 
    "total": 9900,
    "status": "suspended",
    "receipt": "receipt text",
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
    },
    "products": [],
    "subscriptions": [
      {
        "active": true,
        "created_at": 1756245496,
        "expires": true,
        "expires_at": 1758837496,
        "id": 0,
        "in_trial_period": false,
        "subscription": {
          "id": 0,
          "price": 1000,
          "name": "Sample plan",
          "slug": "0-sample-plan",
          "renewal_period": "monthly",
          "interval_unit": "month",
          "interval_count": 1,
          "for_sale": true
        },
        "trial_end_at": null,
        "trial_start_at": null
      }
    ]
  }
}
```

## Plan Events

### subscription_plan.created
Triggered when a new plan is created.

**Pydantic Model:** `SubscriptionPlanCreatedEvent`

```json
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
    "for_sale": true,
    "type": "standard_plan"
  }
}
```

### subscription_plan.updated
Triggered when a plan is updated.

**Pydantic Model:** `SubscriptionPlanUpdatedEvent`

```json
{
  "event": "subscription_plan.updated",
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
```

### subscription_plan.deleted
Triggered when a plan is deleted.

**Pydantic Model:** `SubscriptionPlanDeletedEvent`

```json
{
  "event": "subscription_plan.deleted",
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
```

## Download Events

### download.created
Triggered when a download is created.

**Pydantic Model:** `DownloadCreatedEvent`

```json
{
  "event": "download.created",
  "product": {
    "id": 0,
    "name": "Sample download",
    "price": 1000,
    "slug": "0-sample-download",
    "for_sale": true
  }
}
```

### download.updated
Triggered when a download is updated.

**Pydantic Model:** `DownloadUpdatedEvent`

```json
{
  "event": "download.updated",
  "product": {
    "id": 0,
    "name": "Sample download",
    "price": 1000,
    "slug": "0-sample-download",
    "for_sale": true
  }
}
```

### download.deleted
Triggered when a download is deleted.

**Pydantic Model:** `DownloadDeletedEvent`

```json
{
  "event": "download.deleted",
  "product": {
    "id": 0,
    "name": "Sample download", 
    "price": 1000,
    "slug": "0-sample-download",
    "for_sale": true
  }
}
```

## Usage Examples

### Basic Parsing
```python
from memberful.webhooks import MemberSignupEvent
import json

# Parse a member signup webhook
payload = request.get_data(as_text=True)
data = json.loads(payload)
event = MemberSignupEvent(**data)

print(f"New member: {event.member.email}")
```

### Type-Safe Event Handling
```python
from memberful.webhooks import (
    WebhookEvent, 
    MemberSignupEvent, 
    MemberDeletedEvent,
    SubscriptionCreatedEvent,
    SubscriptionActivatedEvent,
    SubscriptionDeletedEvent,
    SubscriptionRenewedEvent
)

def handle_webhook(event: WebhookEvent):
    if isinstance(event, MemberSignupEvent):
        print(f"Welcome {event.member.email}!")
    elif isinstance(event, MemberDeletedEvent):
        print(f"Member deleted: ID {event.member.id}")
    elif isinstance(event, SubscriptionCreatedEvent):
        print(f"New subscription: {len(event.subscriptions)} subscription(s)")
    elif isinstance(event, SubscriptionActivatedEvent):
        print(f"Subscription activated: {len(event.subscriptions)} subscription(s)")
    elif isinstance(event, SubscriptionDeletedEvent):
        print(f"Subscription deleted: {len(event.subscriptions)} subscription(s)")
    elif isinstance(event, SubscriptionRenewedEvent):
        print(f"Subscription renewed: {len(event.subscriptions)} subscription(s)")
```

## Notes

- **Event Naming**: Note the inconsistent naming convention - member events use underscore format (`member_signup`), while subscription events use dot format (`subscription.created`), and plan events use underscore format (`subscription_plan.created`).

- **Upgrades/Downgrades**: Both upgrades and downgrades trigger the `subscription.updated` webhook. Upgrades include a "changed" section with before/after values. Downgrades may have an empty "changed" section if they occur on the next renewal date.

- **Optional Fields**: Many fields can be null or missing depending on the member's signup method and available data. All Pydantic models handle these gracefully with `Optional` types.

- **Timestamps**: All timestamps are Unix timestamps (seconds since epoch).

- **Prices**: All prices are in the smallest currency unit (e.g., cents for USD).

- **Validation**: All Pydantic models include field validation and will raise `ValidationError` if the webhook payload doesn't match the expected structure.
