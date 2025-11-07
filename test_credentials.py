"""Test script to verify Datadog API credentials."""

import os
from dotenv import load_dotenv
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.logs_list_request import LogsListRequest
from datadog_api_client.v2.model.logs_list_request_page import LogsListRequestPage
from datadog_api_client.v2.model.logs_query_filter import LogsQueryFilter

# Load environment variables
load_dotenv()

print("Testing Datadog API credentials...\n")

# Check if credentials are set
dd_site = os.getenv("DD_SITE")
dd_api_key = os.getenv("DD_API_KEY")
dd_app_key = os.getenv("DD_APP_KEY")

print(f"DD_SITE: {dd_site}")
print(f"DD_API_KEY: {dd_api_key[:8]}...{dd_api_key[-4:] if dd_api_key else 'NOT SET'}")
print(f"DD_APP_KEY: {dd_app_key[:8]}...{dd_app_key[-4:] if dd_app_key else 'NOT SET'}")
print()

if not all([dd_site, dd_api_key, dd_app_key]):
    print("ERROR: Missing required environment variables!")
    exit(1)

# Configure API client
configuration = Configuration()
configuration.api_key["apiKeyAuth"] = dd_api_key
configuration.api_key["appKeyAuth"] = dd_app_key
configuration.server_variables["site"] = dd_site

print("Attempting to connect to Datadog API...")
print(f"API endpoint: https://api.{dd_site}/api/v2/logs/events/search")
print()

try:
    with ApiClient(configuration) as api_client:
        api_instance = LogsApi(api_client)

        # Create a simple test request
        body = LogsListRequest(
            filter=LogsQueryFilter(
                _from="now-5m",
                to="now",
                query="*"
            ),
            page=LogsListRequestPage(limit=1)
        )

        print("Sending test request...")
        response = api_instance.list_logs(body=body)

        print("✅ SUCCESS! API credentials are valid.")
        print(f"Response received with {len(response.data) if hasattr(response, 'data') and response.data else 0} log(s)")

        if hasattr(response, 'data') and response.data:
            print("\nSample log entry:")
            log = response.data[0]
            if hasattr(log, 'attributes'):
                attrs = log.attributes
                print(f"  Timestamp: {getattr(attrs, 'timestamp', 'N/A')}")
                if hasattr(attrs, 'attributes'):
                    print(f"  Service: {attrs.attributes.get('service', 'N/A')}")
                    print(f"  Status: {attrs.attributes.get('status', 'N/A')}")

except Exception as e:
    print(f"❌ FAILED! Error: {e}")
    print()
    print("Common issues:")
    print("1. API Key is invalid or expired")
    print("2. Application Key is invalid or doesn't have 'logs_read_data' scope")
    print("3. DD_SITE is incorrect for your Datadog account")
    print()
    print("To fix:")
    print("- Verify API Key at: https://app.datadoghq.com/organization-settings/api-keys")
    print("- Verify Application Key at: https://app.datadoghq.com/organization-settings/application-keys")
    print("- Ensure Application Key has 'logs_read_data' permission")
