"""Configuration management for Datadog MCP server."""

import os
from typing import Optional
from datadog_api_client import Configuration

CHARACTER_LIMIT = 25000


def validate_config() -> None:
    """
    Validate that all required environment variables are set.

    Raises:
        ValueError: If any required environment variables are missing
    """
    required_vars = ["DD_SITE", "DD_API_KEY", "DD_APP_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Please set them in your environment or .env file. "
            f"See .env.example for reference."
        )


def get_datadog_config() -> Configuration:
    """
    Get configured Datadog API client configuration.

    Returns:
        Configuration: Configured Datadog API client

    Raises:
        ValueError: If required environment variables are not set

    Environment Variables:
        DD_SITE: Datadog site (e.g., datadoghq.com)
        DD_API_KEY: Datadog API key
        DD_APP_KEY: Datadog application key
    """
    validate_config()

    configuration = Configuration()
    configuration.api_key["apiKeyAuth"] = os.getenv("DD_API_KEY")
    configuration.api_key["appKeyAuth"] = os.getenv("DD_APP_KEY")
    configuration.server_variables["site"] = os.getenv("DD_SITE")
    configuration.enable_retry = True

    return configuration


def get_site() -> str:
    """
    Get the configured Datadog site.

    Returns:
        str: The Datadog site (e.g., datadoghq.com)
    """
    return os.getenv("DD_SITE", "datadoghq.com")
