"""Memberful Python client for webhooks and API."""

__version__ = '0.1.0'
__author__ = 'Michael Kennedy'

# Main exports
from .client import MemberfulClient
from .webhooks import WebhookHandler

__all__ = ['MemberfulClient', 'WebhookHandler']
