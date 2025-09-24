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
    SubscriptionDeactivatedEvent,
    SubscriptionDeletedEvent,
    SubscriptionRenewedEvent,
    OrderPurchasedEvent,
    OrderRefundedEvent,
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

Member accounts are created automatically when a member purchases a subscription or [registers for free](https://memberful.com/help/manage-your-members/give-free-access/#enable-free-registration) (if that feature is enabled). You can also [create member accounts manually](https://memberful.com/help/manage-your-members/add-or-delete-a-member/) from your dashboard.

Most webhook types follow the *object.event* naming convention. Member events currently follow an *object_event* convention instead. Pay close attention to the event names laid out in this doc.

### member_signup
Triggered when a new member account is created.

Use this webhook to add new members to your app or to a third-party service.

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
    "created_at": 1758640033,
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
```

### member_updated
Triggered when a member's profile information is updated.

Use this webhook to update a member's profile information in your app.

This will *not* be triggered when a member updates their answers to custom fields. Use the [custom_fields.updated](https://memberful.com/help/custom-development-and-api/webhook-event-reference/#custom_fields-updated) webhook to detect custom field updates.

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
    "created_at": 1758640033,
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
  "changed": {
    "email": [
      "old_email@example.com",
      "john.doe@example.com"
    ]
  }
}
```

### member.deleted
Triggered when a member is deleted from your Memberful account.

Use this webhook to remove a member from your app if they were deleted from Memberful.

It's not common for a member account to be deleted — in most cases, you'll want to react to [Subscription Deactivated](https://memberful.com/help/custom-development-and-api/webhook-event-reference/#subscription-deactivated) instead.

**Pydantic Model:** `MemberDeletedEvent`

**Note:** When a member is deleted, Memberful only sends minimal member information (just the ID and deleted flag), as the full member data is no longer available.

```json
{
  "event": "member.deleted",
  "member": {
    "deleted": true,
    "id": 0
  }
}
```

## Subscription Events

Sent when a member subscribes to a plan or when that subscription is updated, renewed, or deleted.

Almost all times across all webhooks are returned as Unix time, but subscription events use ISO 8601 for the following attributes: `activated_at`, `created_at`, `expires_at`, `trial_end_at`, and `trial_start_at`.

### subscription.created
Triggered when a new subscription is added to a member's account. This includes when a member purchases a subscription or activates a gifted subscription, when a member is added to a group subscription, and when a staff account manually creates a subscription.

Use this webhook to let your app know when a member has subscribed.

**Pydantic Model:** `SubscriptionCreatedEvent`

**Note:** Signups from group managers and members both trigger the **subscription.created** event. To differentiate between the two, you can check the two member IDs in the data that was returned. If both IDs are the same, the signup is from a group manager (or it's for a plan that doesn't support groups). If the IDs are different, the signup is from a member who is joining a group.

```json
{
  "event": "subscription.created",
  "subscription": {
    "active": true,
    "autorenew": true,
    "created_at": "2025-09-23T15:07:13Z",
    "expires_at": "2025-10-23T15:07:13Z",
    "id": 1,
    "member": {
      "address": {
        "street": "Street",
        "city": "City",
        "state": "State",
        "postal_code": "Postal code",
        "country": "City"
      },
      "created_at": 1758640033,
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
    "subscription_plan": {
      "id": 0,
      "interval_count": 1,
      "interval_unit": "month",
      "name": "Sample plan",
      "price_cents": 100000000,
      "slug": "0-sample-plan"
    },
    "trial_end_at": null,
    "trial_start_at": null
  }
}
```

### subscription.updated
Triggered when a member's subscription is updated.

If you want to know if the update is a **plan change,** you'll need to see if the *plan_id* field is present in the *changed* object. The first value is the old plan and the second value is the new one. The same applies to other changed fields, like *autorenew*.

**Pydantic Model:** `SubscriptionUpdatedEvent`

```json
{
  "event": "subscription.updated",
  "subscription": {
    "active": true,
    "autorenew": true,
    "created_at": "2025-09-23T15:07:13Z",
    "expires_at": "2025-10-23T15:07:13Z",
    "id": 1,
    "member": {
      "address": {
        "street": "Street",
        "city": "City",
        "state": "State",
        "postal_code": "Postal code",
        "country": "City"
      },
      "created_at": 1758640033,
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
    "subscription_plan": {
      "id": 0,
      "interval_count": 1,
      "interval_unit": "month",
      "name": "Sample plan",
      "price_cents": 100000000,
      "slug": "0-sample-plan"
    },
    "trial_end_at": null,
    "trial_start_at": null
  },
  "changed": {
    "plan_id": [
      42,
      0
    ],
    "expires_at": [
      "2025-10-23T15:07:13Z",
      "2025-11-22T15:07:13Z"
    ],
    "autorenew": [
      false,
      true
    ]
  }
}
```

### subscription.renewed
Triggered when a member's subscription is renewed or when a returning member reactivates an old subscription.

Use this webhook to renew the member's access to your app. At this time there's no way to differentiate between a renewal and a reactivation, but you could reach out to [our API](https://memberful.com/help/custom-development-and-api/memberful-api/) to find out more about the subscription's history.

**Pydantic Model:** `SubscriptionRenewedEvent`

```json
{
  "event": "subscription.renewed",
  "subscription": {
    "active": true,
    "autorenew": true,
    "created_at": "2025-09-23T15:07:13Z",
    "expires_at": "2025-10-23T15:07:13Z",
    "id": 1,
    "member": {
      "address": {
        "street": "Street",
        "city": "City",
        "state": "State",
        "postal_code": "Postal code",
        "country": "City"
      },
      "created_at": 1758640033,
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
    "subscription_plan": {
      "id": 0,
      "interval_count": 1,
      "interval_unit": "month",
      "name": "Sample plan",
      "price_cents": 100000000,
      "slug": "0-sample-plan"
    },
    "trial_end_at": null,
    "trial_start_at": null
  },
  "order": {
    "created_at": "2025-09-23T15:07:13Z",
    "status": "completed",
    "total": 9900,
    "uuid": "4DACB7B0-B728-0130-F9E8-102B343DC979"
  }
}
```

### subscription.activated
Triggered when a suspended order is marked completed by staff and the subscription becomes active again.

This does *not* refer to when a member reactivates a previously expired subscription — use the [Subscription Renewed](https://memberful.com/help/custom-development-and-api/webhook-event-reference/#subscription-renewed) trigger for that.

**Pydantic Model:** `SubscriptionActivatedEvent`

```json
{
  "event": "subscription.activated",
  "subscription": {
    "active": true,
    "autorenew": true,
    "created_at": "2025-09-23T15:07:13Z",
    "expires_at": "2025-10-23T15:07:13Z",
    "id": 1,
    "member": {
      "address": {
        "street": "Street",
        "city": "City",
        "state": "State",
        "postal_code": "Postal code",
        "country": "City"
      },
      "created_at": 1758640033,
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
    "subscription_plan": {
      "id": 0,
      "interval_count": 1,
      "interval_unit": "month",
      "name": "Sample plan",
      "price_cents": 100000000,
      "slug": "0-sample-plan"
    },
    "trial_end_at": null,
    "trial_start_at": null
  }
}
```

### subscription.deactivated
Triggered when a member's subscription fails to renew, expires, or becomes inactive.

Also sent when a staff account [suspends an order](https://memberful.com/help/manage-your-members/pause-a-subscription/#suspend-the-order), making the subscription inactive.

Use this webhook to remove the member's access to your app or to update their status if they stop paying.

**Pydantic Model:** `SubscriptionDeactivatedEvent`

```json
{
  "event": "subscription.deactivated",
  "subscription": {
    "active": false,
    "autorenew": true,
    "created_at": "2025-09-23T15:07:13Z",
    "expires_at": "2025-10-23T15:07:13Z",
    "id": 1,
    "member": {
      "address": {
        "street": "Street",
        "city": "City",
        "state": "State",
        "postal_code": "Postal code",
        "country": "City"
      },
      "created_at": 1758640033,
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
    "subscription_plan": {
      "id": 0,
      "interval_count": 1,
      "interval_unit": "month",
      "name": "Sample plan",
      "price_cents": 100000000,
      "slug": "0-sample-plan"
    },
    "trial_end_at": null,
    "trial_start_at": null
  }
}
```

### subscription.deleted
Triggered when a staff account deletes a member's subscription from the Memberful dashboard.

Use this webhook to remove the member's access to your app or to update their status.

**Pydantic Model:** `SubscriptionDeletedEvent`

```json
{
  "event": "subscription.deleted",
  "subscription": {
    "active": true,
    "autorenew": true,
    "created_at": "2025-09-23T15:07:13Z",
    "expires_at": "2025-10-23T15:07:13Z",
    "id": 1,
    "member": {
      "address": {
        "street": "Street",
        "city": "City",
        "state": "State",
        "postal_code": "Postal code",
        "country": "City"
      },
      "created_at": 1758640033,
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
    "subscription_plan": {
      "id": 0,
      "interval_count": 1,
      "interval_unit": "month",
      "name": "Sample plan",
      "price_cents": 100000000,
      "slug": "0-sample-plan"
    },
    "trial_end_at": null,
    "trial_start_at": null
  }
}
```

## Order Events

Sent when a member places an order to purchase plans or downloads.

Custom fields are now collected after checkout, which means they're no longer set when the order_purchased event is triggered. To access them, webhook recipients must now use the custom_fields.updated event instead.

### order.purchased
Triggered when a member places an order or when a staff account manually adds an order to a member's account.

This is not triggered for renewal payments.

A member purchasing a gift subscription for someone else will trigger this webhook, but no subscription will be created until the recipient activates their gift.

Use this webhook to notify your app when a member makes a purchase.

**Pydantic Model:** `OrderPurchasedEvent`

```json
{
  "event": "order.purchased",
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
      "created_at": 1758640033,
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
        "created_at": 1758640033,
        "expires": true,
        "expires_at": 1761232033,
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

### order.refunded
Triggered when a staff account refunds an order.

Use this trigger to update your app when a refund has been processed.

**Pydantic Model:** `OrderRefundedEvent`

```json
{
  "event": "order.refunded",
  "order": {
    "uuid": "4DACB7B0-B728-0130-F9E8-102B343DC979",
    "number": "4DACB7B0",
    "total": 9900,
    "status": "refunded",
    "receipt": "receipt text",
    "member": {
      "address": {
        "street": "Street",
        "city": "City",
        "state": "State",
        "postal_code": "Postal code",
        "country": "City"
      },
      "created_at": 1758640033,
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
        "created_at": 1758640033,
        "expires": true,
        "expires_at": 1761232033,
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
      "created_at": 1758640033,
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
        "created_at": 1758640033,
        "expires": true,
        "expires_at": 1761232033,
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
      "created_at": 1758640033,
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
        "created_at": 1758640033,
        "expires": true,
        "expires_at": 1761232033,
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

Sent when staff accounts create, update, or delete plans.

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
    "for_sale": true
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

Staff can create downloads to include with plans or to sell separately.

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
from memberful.webhooks import parse_payload, validate_signature
import json

# Complete webhook handling with signature validation
def handle_webhook(request_body: str, signature_header: str, webhook_secret: str):
    # 1. Validate the webhook signature
    if not validate_signature(request_body, signature_header, webhook_secret):
        raise ValueError("Invalid webhook signature")
    
    # 2. Parse the payload into a strongly-typed event
    data = json.loads(request_body)
    event = parse_payload(data)
    
    print(f"Received {event.event} event")
    return event

# Alternative: Direct parsing (if you've already validated signature elsewhere)
from memberful.webhooks import MemberSignupEvent

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
    SubscriptionDeactivatedEvent,
    SubscriptionDeletedEvent,
    SubscriptionRenewedEvent,
    OrderPurchasedEvent,
    OrderRefundedEvent,
    OrderCompletedEvent,
    OrderSuspendedEvent
)

def handle_webhook(event: WebhookEvent):
    if isinstance(event, MemberSignupEvent):
        print(f"Welcome {event.member.email}!")
    elif isinstance(event, MemberDeletedEvent):
        print(f"Member deleted: ID {event.member.id}")
    elif isinstance(event, SubscriptionCreatedEvent):
        print(f"New subscription: {event.subscription.subscription_plan.name}")
    elif isinstance(event, SubscriptionActivatedEvent):
        print(f"Subscription activated: {event.subscription.subscription_plan.name}")
    elif isinstance(event, SubscriptionDeactivatedEvent):
        print(f"Subscription deactivated: {event.subscription.subscription_plan.name}")
    elif isinstance(event, SubscriptionDeletedEvent):
        print(f"Subscription deleted: {event.subscription.subscription_plan.name}")
    elif isinstance(event, SubscriptionRenewedEvent):
        print(f"Subscription renewed: {event.subscription.subscription_plan.name}")
    elif isinstance(event, (OrderPurchasedEvent, OrderRefundedEvent, OrderCompletedEvent, OrderSuspendedEvent)):
        print(f"Order {event.event}: {event.order.uuid}")
```

## How upgrades/downgrades are handled

Both upgrades and downgrades trigger the [subscription.updated webhook](https://memberful.com/help/custom-development-and-api/webhook-event-reference/#subscription-updated).

Upgrades include a "changed" section detailing the changes:

```json
"changed": {
  "plan_id": [
    42,
    0
  ],
  "expires_at": [
    "2023-05-12T15:09:58Z",
    "2023-06-11T15:09:58Z"
  ],
  "autorenew": [
    false,
    true
  ]
}
```

Downgrades tend to happen on the next renewal date (since the member already paid a higher price for their current period, they're not downgraded immediately). In that case, the "changed" section will be empty.

## Notes

- **Event Naming**: Note the inconsistent naming convention - member events use underscore format (`member_signup`), while subscription events use dot format (`subscription.created`), and plan events use underscore format (`subscription_plan.created`).

- **Subscription Event Structure**: Subscription events include a top-level `subscription` object with full member data and subscription plan details, using ISO 8601 datetime strings for timestamps.

- **Order Event Structure**: Order events include a top-level `order` object with embedded member data and related subscriptions/products, using Unix timestamps for member data and mixed formats for order data.

- **Optional Fields**: Many fields can be null or missing depending on the member's signup method and available data. All Pydantic models handle these gracefully with `Optional` types.

- **Timestamps**: Member timestamps are Unix timestamps (seconds since epoch). Subscription event timestamps use ISO 8601 format.

- **Prices**: All prices are in the smallest currency unit (e.g., cents for USD). Note that subscription plans may use either `price` or `price_cents` field names.

- **Validation**: All Pydantic models include field validation and will raise `ValidationError` if the webhook payload doesn't match the expected structure.