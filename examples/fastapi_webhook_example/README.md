# Memberful FastAPI Webhook Example

This example demonstrates how to create a FastAPI application that handles all Memberful webhook events using the existing webhook models and parsing functionality from the `memberful` package.

## Features

- ✅ Handles all 12 Memberful webhook event types
- ✅ Type-safe webhook parsing using Pydantic models
- ✅ RESTful API with health check endpoint
- ✅ Auto-generated API documentation
- ✅ Detailed logging of webhook events
- ✅ Proper error handling and HTTP status codes

## Supported Webhook Events

The app handles these Memberful webhook event types:

- `member_signup` - New member registration
- `member_updated` - Member profile updates  
- `subscription.created` - New subscription
- `subscription.updated` - Subscription changes
- `order.completed` - Order completion
- `order.suspended` - Order suspension
- `subscription_plan.created` - New subscription plan
- `subscription_plan.updated` - Plan modifications
- `subscription_plan.deleted` - Plan deletion
- `download.created` - New download/product
- `download.updated` - Product updates
- `download.deleted` - Product deletion

## Installation

1. Navigate to the example directory:
   ```bash
   cd examples/fastapi_webhook_example
   ```

2. Install dependencies:
   ```bash
   # Install FastAPI and dependencies
   pip install -r requirements.txt
   
   # Install the memberful package in development mode
   pip install -e ../../
   ```

## Running the Application

Start the FastAPI development server:

```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The app will start on `http://localhost:8000` with these endpoints:

- **Main webhook endpoint**: `POST /webhook`
- **Health check**: `GET /health`
- **Root info**: `GET /`
- **API docs**: `GET /docs` (Swagger UI)
- **OpenAPI schema**: `GET /openapi.json`

## Testing the Webhook Handler

### Using curl

Send a test webhook payload:

```bash
curl -X POST "http://localhost:8000/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "member_signup",
    "member": {
      "id": 12345,
      "email": "test@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "created_at": 1640995200,
      "signup_method": "checkout",
      "unrestricted_access": false
    }
  }'
```

### Using Python requests

```python
import requests

payload = {
    "event": "subscription.created",
    "member": {
        "id": 12345,
        "email": "customer@example.com",
        "first_name": "Jane",
        "created_at": 1640995200,
        "unrestricted_access": False
    },
    "subscriptions": [
        {
            "id": 67890,
            "active": True,
            "created_at": 1640995200,
            "expires": True,
            "expires_at": 1672531200,
            "in_trial_period": False,
            "subscription": {
                "id": 42,
                "name": "Premium Plan",
                "price": 2999,
                "slug": "premium",
                "renewal_period": "monthly",
                "interval_unit": "month",
                "interval_count": 1,
                "for_sale": True
            }
        }
    ],
    "products": []
}

response = requests.post("http://localhost:8000/webhook", json=payload)
print(response.json())
```

## What Happens When a Webhook is Received

1. **Request Processing**: The FastAPI app receives the webhook POST request at `/webhook`
2. **JSON Parsing**: The raw request body is parsed as JSON
3. **Event Type Detection**: The `event` field determines which Pydantic model to use
4. **Model Validation**: The payload is validated and parsed into the appropriate event model
5. **Event Handling**: The event is routed to a specific handler function that prints detailed information
6. **Response**: A success response is returned with the event type and status

## Console Output Example

When a webhook is received, you'll see detailed output like:

```
[2024-01-15 14:30:25] Processing webhook event: member_signup
------------------------------------------------------------
🎉 [MEMBER SIGNUP] New member signed up: test@example.com
   Welcome, John!
   Member ID: 12345
   Signup method: checkout
------------------------------------------------------------
```

## Integration with Memberful

To receive real webhooks from Memberful:

1. **Configure webhook URL** in your Memberful admin dashboard
2. **Set endpoint** to your server's `/webhook` URL (e.g., `https://yourapp.com/webhook`)
3. **Select events** you want to receive
4. **Optional**: Add webhook signature verification (see Memberful docs)

## Customization

This example simply prints webhook details to the console. In a real application, you might:

- Store webhook data in a database
- Send notifications or emails
- Trigger business logic
- Update external systems
- Queue background jobs

You can modify the handler functions in `main.py` to implement your specific business logic.

## Error Handling

The app includes proper error handling for:

- Invalid JSON payloads (400 Bad Request)
- Unsupported event types (400 Bad Request)
- Pydantic validation errors (400 Bad Request)
- Unexpected server errors (500 Internal Server Error)

## Development

For development, the app includes:

- Hot reloading with `--reload` flag
- Detailed error messages and stack traces
- Auto-generated API documentation at `/docs`
- Health check endpoint for monitoring
