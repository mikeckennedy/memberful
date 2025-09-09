"""Memberful Python client for webhooks and API.

Use the submodules to access functionality:
- memberful.api: API client (MemberfulClient)
- memberful.webhooks: Webhook handling (parse_payload, validate_signature, event models)
"""

__version__ = '0.1.0'
__author__ = 'Michael Kennedy'

# Import submodules - users must access functionality through these
from . import api, webhooks

__all__ = [
    'api',  # API submodule
    'webhooks',  # Webhooks submodule
]
