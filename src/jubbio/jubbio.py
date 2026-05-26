"""
Public entry point for the unified Jubbio Python client.

This module intentionally re-exports the main classes so users can do:

    from jubbio.jubbio import Client
"""

from .client import Client

__all__ = ["Client"]

