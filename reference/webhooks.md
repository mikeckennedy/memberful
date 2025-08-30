# Memberful Webhook Events Reference

This document contains the JSON structures for all Memberful webhook events as documented at [Memberful Webhook Event Reference](https://memberful.com/help/custom-development-and-api/webhook-event-reference/).

## Member Events

### member_signup
Triggered when a new member account is created.

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
Triggered when a member is updated.

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
```

## Subscription Events

### subscription.created
Triggered when a new subscription is created.

```json
{
  "event": "subscription.created",
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
```

### subscription.updated
Triggered when a subscription is updated (including upgrades and downgrades).

```json
{
  "event": "subscription.updated",
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
  ],
  "changed": {
    "plan_id": [42, 0],
    "expires_at": ["2023-05-12T15:09:58Z", "2023-06-11T15:09:58Z"],
    "autorenew": [false, true]
  }
}
```

## Order Events

### order.completed
Triggered when a suspended order is marked completed by staff.

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

## Notes

- **Event Naming**: Note the inconsistent naming convention - member events use underscore format (`member_signup`), while subscription events use dot format (`subscription.created`), and plan events use underscore format (`subscription_plan.created`).

- **Upgrades/Downgrades**: Both upgrades and downgrades trigger the `subscription.updated` webhook. Upgrades include a "changed" section with before/after values. Downgrades may have an empty "changed" section if they occur on the next renewal date.

- **Optional Fields**: Many fields can be null or missing depending on the member's signup method and available data.

- **Timestamps**: All timestamps are Unix timestamps (seconds since epoch).

- **Prices**: All prices are in the smallest currency unit (e.g., cents for USD).
