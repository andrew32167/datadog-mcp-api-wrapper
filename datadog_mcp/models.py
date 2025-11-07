"""Pydantic models for input validation."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class ResponseFormat(str, Enum):
    """Response format options."""

    MARKDOWN = "markdown"
    JSON = "json"


class SearchLogsInput(BaseModel):
    """
    Input model for searching Datadog logs.

    Attributes:
        query: Search query using Datadog syntax
        from_time: Start time for the search range
        to_time: End time for the search range
        limit: Maximum number of results to return
        response_format: Output format (markdown or json)
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )

    query: str = Field(
        ...,
        description=(
            "Search query using Datadog syntax. "
            "Examples: 'status:error', 'service:web-app AND status:error', "
            "'@http.status_code:500', 'env:production error'"
        ),
        min_length=1,
        max_length=500
    )

    from_time: str = Field(
        default="now-15m",
        description=(
            "Start time for the search range. "
            "Supports ISO8601 format (e.g., '2024-01-01T00:00:00Z'), "
            "date math (e.g., 'now-15m', 'now-1h', 'now-1d'), "
            "or epoch milliseconds"
        ),
        alias="from"
    )

    to_time: str = Field(
        default="now",
        description=(
            "End time for the search range. "
            "Supports same formats as from_time"
        ),
        alias="to"
    )

    limit: int = Field(
        default=50,
        description="Maximum number of results to return",
        ge=1,
        le=1000
    )

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description=(
            "Output format. "
            "'markdown' for human-readable formatted output, "
            "'json' for structured machine-readable output"
        )
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """
        Validate that query is not empty after stripping whitespace.

        Args:
            v: Query string to validate

        Returns:
            str: Validated and stripped query string

        Raises:
            ValueError: If query is empty
        """
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class SearchTracesInput(BaseModel):
    """
    Input model for searching Datadog traces/spans.

    Attributes:
        query: Search query using Datadog syntax
        from_time: Start time for the search range
        to_time: End time for the search range
        limit: Maximum number of results to return
        response_format: Output format (markdown or json)
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )

    query: str = Field(
        ...,
        description=(
            "Search query using Datadog syntax. "
            "Examples: 'service:web-app', 'service:python* @http.status_code:500', "
            "'resource_name:GET /api/users', 'error:true'"
        ),
        min_length=1,
        max_length=500
    )

    from_time: str = Field(
        default="now-15m",
        description=(
            "Start time for the search range. "
            "Supports ISO8601 format (e.g., '2024-01-01T00:00:00Z'), "
            "date math (e.g., 'now-15m', 'now-1h', 'now-1d'), "
            "or epoch milliseconds"
        ),
        alias="from"
    )

    to_time: str = Field(
        default="now",
        description=(
            "End time for the search range. "
            "Supports same formats as from_time"
        ),
        alias="to"
    )

    limit: int = Field(
        default=50,
        description="Maximum number of results to return",
        ge=1,
        le=1000
    )

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description=(
            "Output format. "
            "'markdown' for human-readable formatted output, "
            "'json' for structured machine-readable output"
        )
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """
        Validate that query is not empty after stripping whitespace.

        Args:
            v: Query string to validate

        Returns:
            str: Validated and stripped query string

        Raises:
            ValueError: If query is empty
        """
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()
