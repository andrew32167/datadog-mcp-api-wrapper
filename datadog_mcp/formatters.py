"""Response formatting utilities for Datadog API results."""

import json
from typing import Any, Dict
from datetime import datetime

from datadog_mcp.config import CHARACTER_LIMIT


def format_timestamp(timestamp: Any) -> str:
    """
    Format a timestamp value into a human-readable string.

    Args:
        timestamp: Timestamp value (can be ISO string, epoch ms, or None)

    Returns:
        str: Formatted timestamp string or "N/A"
    """
    if timestamp is None:
        return "N/A"

    if isinstance(timestamp, str):
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except (ValueError, AttributeError):
            return timestamp

    if isinstance(timestamp, (int, float)):
        try:
            dt = datetime.fromtimestamp(timestamp / 1000.0)
            return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except (ValueError, OSError):
            return str(timestamp)

    return str(timestamp)


def format_logs_markdown(result: Dict[str, Any], query: str) -> str:
    """
    Format logs search results as Markdown.

    Args:
        result: Result dictionary from search_logs_api
        query: The original search query

    Returns:
        str: Markdown-formatted search results
    """
    logs = result.get("logs", [])
    total = result.get("total", 0)
    has_more = result.get("has_more", False)

    lines = [
        f"# Log Search Results",
        f"",
        f"**Query:** `{query}`",
        f"**Results:** Found {total} log(s)",
        f""
    ]

    if not logs:
        lines.append("No logs found matching the query.")
        return "\n".join(lines)

    for i, log in enumerate(logs, 1):
        timestamp = format_timestamp(log.get("timestamp"))
        service = log.get("service") or "unknown"
        status = log.get("status") or "unknown"
        message = log.get("message") or "No message"
        host = log.get("host")
        trace_id = log.get("trace_id")
        span_id = log.get("span_id")

        lines.append(f"## Log {i}: {service}")
        lines.append(f"")
        lines.append(f"- **Timestamp:** {timestamp}")
        lines.append(f"- **Status:** {status}")
        if host:
            lines.append(f"- **Host:** {host}")
        lines.append(f"- **Message:** {message}")

        if trace_id:
            lines.append(f"- **Trace ID:** {trace_id}")
        if span_id:
            lines.append(f"- **Span ID:** {span_id}")

        tags = log.get("tags", [])
        if tags:
            tags_str = ", ".join(tags[:10])
            if len(tags) > 10:
                tags_str += f" ... (+{len(tags) - 10} more)"
            lines.append(f"- **Tags:** {tags_str}")

        lines.append(f"")

    if has_more:
        lines.append("---")
        lines.append("")
        lines.append("**Note:** More results available. The API returned a pagination cursor.")

    return "\n".join(lines)


def format_logs_json(result: Dict[str, Any]) -> str:
    """
    Format logs search results as JSON.

    Args:
        result: Result dictionary from search_logs_api

    Returns:
        str: JSON-formatted search results
    """
    return json.dumps(result, indent=2, default=str)


def format_traces_markdown(result: Dict[str, Any], query: str) -> str:
    """
    Format traces/spans search results as Markdown.

    Args:
        result: Result dictionary from search_traces_api
        query: The original search query

    Returns:
        str: Markdown-formatted search results
    """
    spans = result.get("spans", [])
    total = result.get("total", 0)
    has_more = result.get("has_more", False)

    lines = [
        f"# Trace/Span Search Results",
        f"",
        f"**Query:** `{query}`",
        f"**Results:** Found {total} span(s)",
        f""
    ]

    if not spans:
        lines.append("No traces/spans found matching the query.")
        return "\n".join(lines)

    for i, span in enumerate(spans, 1):
        timestamp = format_timestamp(span.get("timestamp"))
        service = span.get("service") or "unknown"
        resource = span.get("resource") or "unknown"
        operation = span.get("operation") or "unknown"
        duration = span.get("duration")
        error = span.get("error", False)
        trace_id = span.get("trace_id")
        span_id = span.get("span_id")

        lines.append(f"## Span {i}: {service} - {operation}")
        lines.append(f"")
        lines.append(f"- **Timestamp:** {timestamp}")
        lines.append(f"- **Service:** {service}")
        lines.append(f"- **Resource:** {resource}")
        lines.append(f"- **Operation:** {operation}")

        if duration is not None:
            duration_ms = duration / 1_000_000
            lines.append(f"- **Duration:** {duration_ms:.2f} ms")

        lines.append(f"- **Error:** {'Yes' if error else 'No'}")

        if trace_id:
            lines.append(f"- **Trace ID:** {trace_id}")
        if span_id:
            lines.append(f"- **Span ID:** {span_id}")

        tags = span.get("tags", [])
        if tags:
            tags_str = ", ".join(tags[:10])
            if len(tags) > 10:
                tags_str += f" ... (+{len(tags) - 10} more)"
            lines.append(f"- **Tags:** {tags_str}")

        lines.append(f"")

    if has_more:
        lines.append("---")
        lines.append("")
        lines.append("**Note:** More results available. The API returned a pagination cursor.")

    return "\n".join(lines)


def format_traces_json(result: Dict[str, Any]) -> str:
    """
    Format traces/spans search results as JSON.

    Args:
        result: Result dictionary from search_traces_api

    Returns:
        str: JSON-formatted search results
    """
    return json.dumps(result, indent=2, default=str)


def truncate_response(response: str, params: Any) -> str:
    """
    Truncate response if it exceeds CHARACTER_LIMIT.

    Args:
        response: The formatted response string
        params: Input parameters (used to provide helpful guidance)

    Returns:
        str: Original or truncated response with truncation message
    """
    if len(response) <= CHARACTER_LIMIT:
        return response

    truncation_point = CHARACTER_LIMIT - 500
    truncated = response[:truncation_point]

    limit = getattr(params, "limit", 50)

    truncation_message = f"""

---

**Response Truncated**

The response exceeded the {CHARACTER_LIMIT:,} character limit and has been truncated.

**Suggestions to see more results:**
- Reduce the `limit` parameter (currently: {limit})
- Add more specific filters to your query
- Narrow the time range with `from` and `to` parameters
- Use pagination with the cursor if available
"""

    return truncated + truncation_message
