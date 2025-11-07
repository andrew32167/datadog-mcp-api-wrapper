"""Error handling utilities for Datadog API interactions."""

from datadog_api_client.exceptions import ApiException


def handle_api_error(e: Exception) -> str:
    """
    Convert API exceptions into user-friendly error messages.

    Args:
        e: The exception that was raised

    Returns:
        str: A user-friendly error message with actionable guidance

    Examples:
        >>> handle_api_error(ApiException(status=403))
        'Error: Permission denied. Check your DD_API_KEY and DD_APP_KEY...'
    """
    if isinstance(e, ApiException):
        status = e.status

        if status == 400:
            return (
                f"Error: Bad request - {e.reason}. "
                "Check your query syntax and parameters. "
                "See https://docs.datadoghq.com/logs/explorer/search_syntax/ for query syntax."
            )
        elif status == 403:
            return (
                "Error: Permission denied. Check your DD_API_KEY and DD_APP_KEY "
                "environment variables. Ensure the API key has the required permissions "
                "for logs and traces access."
            )
        elif status == 404:
            return (
                "Error: Resource not found. The requested resource does not exist "
                "or you don't have permission to access it."
            )
        elif status == 429:
            return (
                "Error: Rate limit exceeded. Please wait before retrying. "
                "Traces API has a limit of 300 requests per hour. "
                "Consider reducing the frequency of requests or using more specific queries."
            )
        elif status >= 500:
            return (
                f"Error: Datadog API server error ({status}). "
                "This is a temporary issue with the Datadog service. "
                "Please try again in a few moments."
            )
        else:
            return f"Error: API request failed with status {status}: {e.reason}"

    elif isinstance(e, TimeoutError):
        return (
            "Error: Request timed out. The Datadog API did not respond in time. "
            "Try reducing the time range or adding more specific filters to your query."
        )
    elif isinstance(e, ConnectionError):
        return (
            "Error: Connection failed. Unable to reach the Datadog API. "
            "Check your network connection and ensure DD_SITE is configured correctly."
        )
    else:
        error_type = type(e).__name__
        error_msg = str(e)
        return f"Error: Unexpected {error_type}: {error_msg}"
