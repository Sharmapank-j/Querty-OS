"""Querty-OS CLI and API Package"""

from .api import QuertyAPI, create_api
from .cli import cli

__version__ = "0.1.0"
__all__ = ["cli", "QuertyAPI", "create_api"]
