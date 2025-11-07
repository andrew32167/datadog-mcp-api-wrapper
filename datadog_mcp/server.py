"""Datadog MCP Server - Main server implementation."""
import os
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from datadog_mcp.models import SearchLogsInput, SearchTracesInput, ResponseFormat
from datadog_mcp.client import search_logs_api, search_traces_api
from datadog_mcp.formatters import (
    format_logs_markdown,
    format_logs_json,
    format_traces_markdown,
    format_traces_json,
    truncate_response
)
from datadog_mcp.errors import handle_api_error
from datadog_mcp.config import validate_config

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

mcp = FastMCP("datadog_mcp")


@mcp.tool(
    name="datadog_search_logs",
    annotations={
        "title": "Search Datadog Logs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def datadog_search_logs(params: SearchLogsInput) -> str:
    """
    Search for logs in Datadog by query, time range, and filters.

    This tool searches across all log data in the configured Datadog site,
    supporting the full Datadog query syntax with time range filtering.
    Results can be returned in human-readable Markdown format or structured JSON.

    Args:
        params (SearchLogsInput): Validated input parameters containing:
            - query (str): Search query using Datadog syntax
                Examples: "status:error", "service:web-app AND status:error",
                         "@http.status_code:500", "env:production error"
            - from_time (str): Start time (default: "now-15m")
                Supports ISO8601 format, date math (e.g., "now-1h", "now-1d"),
                or epoch milliseconds
            - to_time (str): End time (default: "now")
                Same formats as from_time
            - limit (int): Maximum results to return (default: 50, max: 1000)
            - response_format (ResponseFormat): Output format (default: markdown)
                "markdown" for human-readable formatted output
                "json" for structured machine-readable output

    Returns:
        str: Formatted search results based on response_format parameter

        Markdown format shows:
        - Query summary with result count
        - Each log entry with timestamp, service, status, host, and message
        - Tags (up to 10 per log)
        - Pagination indicator if more results available

        JSON format includes:
        {
            "total": int,           # Total number of results
            "count": int,           # Number of results returned
            "logs": [...],          # Array of log objects
            "has_more": bool,       # Whether more results are available
            "next_cursor": str|null # Pagination cursor for next page
        }

    Examples:
        Search for recent errors:
            query="status:error"
            from_time="now-1h"

        Search specific service with time range:
            query="service:web-app AND @http.status_code:500"
            from_time="2024-01-01T00:00:00Z"
            to_time="2024-01-01T23:59:59Z"

        Get JSON output for programmatic processing:
            query="env:production error"
            response_format="json"

    Error Handling:
        - Returns clear error messages for common issues:
          - "Permission denied" if API credentials are invalid
          - "Rate limit exceeded" if API rate limit is hit
          - "Bad request" if query syntax is invalid
          - "Request timed out" if API doesn't respond in time
        - Automatically truncates responses exceeding 25,000 characters
          with helpful guidance on reducing result size

    Query Syntax:
        Datadog log search supports:
        - Simple text: "error"
        - Field search: "service:web-app"
        - Boolean operators: "service:web AND status:error"
        - Wildcards: "service:python*"
        - Facets: "@http.status_code:500"
        - Tags: "env:production"

        See: https://docs.datadoghq.com/logs/explorer/search_syntax/

    Rate Limits:
        The Logs API has generous rate limits. If you encounter rate limiting,
        the error message will provide guidance on retry timing.
    """
    try:
        result = await search_logs_api(params)

        if params.response_format == ResponseFormat.MARKDOWN:
            formatted = format_logs_markdown(result, params.query)
        else:
            formatted = format_logs_json(result)

        return truncate_response(formatted, params)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="datadog_search_traces",
    annotations={
        "title": "Search Datadog Traces",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def datadog_search_traces(params: SearchTracesInput) -> str:
    """
    Search for traces and spans in Datadog by query, time range, and filters.

    This tool searches across all trace/span data in the configured Datadog site,
    supporting the full Datadog query syntax with time range filtering.
    Results can be returned in human-readable Markdown format or structured JSON.

    Args:
        params (SearchTracesInput): Validated input parameters containing:
            - query (str): Search query using Datadog syntax
                Examples: "service:web-app", "service:python* @http.status_code:500",
                         "resource_name:GET /api/users", "error:true"
            - from_time (str): Start time (default: "now-15m")
                Supports ISO8601 format, date math (e.g., "now-1h", "now-1d"),
                or epoch milliseconds
            - to_time (str): End time (default: "now")
                Same formats as from_time
            - limit (int): Maximum results to return (default: 50, max: 1000)
            - response_format (ResponseFormat): Output format (default: markdown)
                "markdown" for human-readable formatted output
                "json" for structured machine-readable output

    Returns:
        str: Formatted search results based on response_format parameter

        Markdown format shows:
        - Query summary with result count
        - Each span with timestamp, service, resource, operation, duration
        - Error status and trace/span IDs
        - Tags (up to 10 per span)
        - Pagination indicator if more results available

        JSON format includes:
        {
            "total": int,           # Total number of results
            "count": int,           # Number of results returned
            "spans": [...],         # Array of span objects
            "has_more": bool,       # Whether more results are available
            "next_cursor": str|null # Pagination cursor for next page
        }

    Examples:
        Search for recent errors in a service:
            query="service:web-app error:true"
            from_time="now-1h"

        Find slow API calls:
            query="resource_name:GET /api/* @duration:>1000000000"
            from_time="now-30m"

        Get JSON output for analysis:
            query="service:python*"
            response_format="json"

    Error Handling:
        - Returns clear error messages for common issues:
          - "Permission denied" if API credentials are invalid
          - "Rate limit exceeded" if API rate limit is hit (300 requests/hour)
          - "Bad request" if query syntax is invalid
          - "Request timed out" if API doesn't respond in time
        - Automatically truncates responses exceeding 25,000 characters
          with helpful guidance on reducing result size

    Query Syntax:
        Datadog trace search supports:
        - Simple text: "error"
        - Field search: "service:web-app"
        - Boolean operators: "service:web AND error:true"
        - Wildcards: "service:python*"
        - Facets: "@http.status_code:500"
        - Resource: "resource_name:GET /api/users"
        - Duration: "@duration:>1000000000" (in nanoseconds)

        See: https://docs.datadoghq.com/tracing/trace_explorer/query_syntax/

    Rate Limits:
        IMPORTANT: The Traces API has a rate limit of 300 requests per hour.
        If you exceed this limit, you'll receive a clear error message with
        retry guidance. Consider using more specific queries to reduce the
        number of requests needed.
    """
    try:
        result = await search_traces_api(params)

        if params.response_format == ResponseFormat.MARKDOWN:
            formatted = format_traces_markdown(result, params.query)
        else:
            formatted = format_traces_json(result)

        return truncate_response(formatted, params)

    except Exception as e:
        return handle_api_error(e)


if __name__ == "__main__":
    try:
        validate_config()
        mcp.run()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nPlease ensure the following environment variables are set:")
        print("  - DD_SITE (e.g., datadoghq.com)")
        print("  - DD_API_KEY")
        print("  - DD_APP_KEY")
        print("\nSee .env.example for reference.")
        exit(1)
