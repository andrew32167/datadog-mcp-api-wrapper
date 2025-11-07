"""Datadog API client wrapper functions."""

from typing import Any, Dict
from datadog_api_client import ApiClient
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.api.spans_api import SpansApi
from datadog_api_client.v2.model.logs_list_request import LogsListRequest
from datadog_api_client.v2.model.logs_list_request_page import LogsListRequestPage
from datadog_api_client.v2.model.logs_query_filter import LogsQueryFilter
from datadog_api_client.v2.model.logs_sort import LogsSort
from datadog_api_client.v2.model.spans_list_request import SpansListRequest
from datadog_api_client.v2.model.spans_list_request_data import SpansListRequestData
from datadog_api_client.v2.model.spans_list_request_attributes import SpansListRequestAttributes
from datadog_api_client.v2.model.spans_list_request_page import SpansListRequestPage
from datadog_api_client.v2.model.spans_query_filter import SpansQueryFilter
from datadog_api_client.v2.model.spans_sort import SpansSort

from datadog_mcp.models import SearchLogsInput, SearchTracesInput
from datadog_mcp.config import get_datadog_config


def build_logs_request(params: SearchLogsInput) -> LogsListRequest:
    """
    Build a Datadog logs list request from input parameters.

    Args:
        params: Validated search input parameters

    Returns:
        LogsListRequest: Configured request object for Datadog Logs API
    """
    query_filter = LogsQueryFilter(
        _from=params.from_time,
        to=params.to_time,
        query=params.query
    )

    page = LogsListRequestPage(limit=params.limit)

    return LogsListRequest(
        filter=query_filter,
        page=page,
        sort=LogsSort.TIMESTAMP_DESCENDING
    )


def build_traces_request(params: SearchTracesInput) -> SpansListRequest:
    """
    Build a Datadog spans list request from input parameters.

    Args:
        params: Validated search input parameters

    Returns:
        SpansListRequest: Configured request object for Datadog Spans API
    """
    query_filter = SpansQueryFilter(
        _from=params.from_time,
        to=params.to_time,
        query=params.query
    )

    page = SpansListRequestPage(limit=params.limit)

    attributes = SpansListRequestAttributes(
        filter=query_filter,
        page=page,
        sort=SpansSort.TIMESTAMP_DESCENDING
    )

    data = SpansListRequestData(
        attributes=attributes,
        type="search_request"
    )

    return SpansListRequest(data=data)


async def search_logs_api(params: SearchLogsInput) -> Dict[str, Any]:
    """
    Execute a logs search via the Datadog API.

    Args:
        params: Validated search input parameters

    Returns:
        Dict containing logs data and metadata

    Raises:
        ApiException: If the API request fails
    """
    config = get_datadog_config()

    with ApiClient(config) as api_client:
        api_instance = LogsApi(api_client)
        body = build_logs_request(params)
        response = api_instance.list_logs(body=body)

        logs_data = []
        if hasattr(response, "data") and response.data:
            for log in response.data:
                log_dict = {
                    "id": log.id if hasattr(log, "id") else None,
                    "timestamp": None,
                    "message": None,
                    "service": None,
                    "status": None,
                    "host": None,
                    "trace_id": None,
                    "span_id": None,
                    "tags": []
                }

                if hasattr(log, "attributes") and log.attributes:
                    attrs = log.attributes
                    log_dict["timestamp"] = getattr(attrs, "timestamp", None)
                    log_dict["message"] = getattr(attrs, "message", None)

                    if hasattr(attrs, "attributes"):
                        custom_attrs = attrs.attributes
                        log_dict["service"] = custom_attrs.get("service")
                        log_dict["status"] = custom_attrs.get("status")
                        log_dict["host"] = custom_attrs.get("host")
                        log_dict["trace_id"] = custom_attrs.get("dd.trace_id") or custom_attrs.get("trace_id")
                        log_dict["span_id"] = custom_attrs.get("dd.span_id") or custom_attrs.get("span_id")

                    if hasattr(attrs, "tags"):
                        log_dict["tags"] = attrs.tags or []

                logs_data.append(log_dict)

        result = {
            "total": len(logs_data),
            "count": len(logs_data),
            "logs": logs_data,
            "has_more": False,
            "next_cursor": None
        }

        if hasattr(response, "meta") and response.meta:
            if hasattr(response.meta, "page") and response.meta.page:
                result["next_cursor"] = getattr(response.meta.page, "after", None)
                result["has_more"] = bool(result["next_cursor"])

        return result


async def search_traces_api(params: SearchTracesInput) -> Dict[str, Any]:
    """
    Execute a traces/spans search via the Datadog API.

    Args:
        params: Validated search input parameters

    Returns:
        Dict containing spans data and metadata

    Raises:
        ApiException: If the API request fails
    """
    config = get_datadog_config()

    with ApiClient(config) as api_client:
        api_instance = SpansApi(api_client)
        body = build_traces_request(params)
        response = api_instance.list_spans(body=body)

        spans_data = []
        if hasattr(response, "data") and response.data:
            for span in response.data:
                span_dict = {
                    "span_id": None,
                    "trace_id": None,
                    "timestamp": None,
                    "service": None,
                    "resource": None,
                    "operation": None,
                    "duration": None,
                    "error": False,
                    "tags": []
                }

                if hasattr(span, "attributes") and span.attributes:
                    attrs = span.attributes
                    span_dict["span_id"] = getattr(attrs, "span_id", None)
                    span_dict["trace_id"] = getattr(attrs, "trace_id", None)
                    span_dict["timestamp"] = getattr(attrs, "start", None)

                    if hasattr(attrs, "attributes"):
                        custom_attrs = attrs.attributes
                        span_dict["service"] = custom_attrs.get("service")
                        span_dict["resource"] = custom_attrs.get("resource_name")
                        span_dict["operation"] = custom_attrs.get("operation_name")
                        span_dict["duration"] = custom_attrs.get("duration")
                        span_dict["error"] = custom_attrs.get("error", False)

                    if hasattr(attrs, "tags"):
                        span_dict["tags"] = attrs.tags or []

                spans_data.append(span_dict)

        result = {
            "total": len(spans_data),
            "count": len(spans_data),
            "spans": spans_data,
            "has_more": False,
            "next_cursor": None
        }

        if hasattr(response, "meta") and response.meta:
            if hasattr(response.meta, "page") and response.meta.page:
                result["next_cursor"] = getattr(response.meta.page, "after", None)
                result["has_more"] = bool(result["next_cursor"])

        return result
