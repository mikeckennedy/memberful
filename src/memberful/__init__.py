"""Memberful Python client for webhooks and API.

Use the submodules to access functionality:
- memberful.api: API client (MemberfulClient)
- memberful.webhooks: Webhook handling (parse_payload, validate_signature, event models)
"""

from importlib.metadata import PackageNotFoundError, version

# pyproject.toml is the single source of the version; read it from the installed package's metadata.
try:
    __version__ = version('memberful')
except PackageNotFoundError:  # pragma: no cover - running from a source tree that isn't installed
    __version__ = '0.0.0+unknown'
__author__ = 'Michael Kennedy'

# Import submodules - users must access functionality through these
from . import api, webhooks

__all__ = [
    'api',  # API submodule
    'webhooks',  # Webhooks submodule
]
