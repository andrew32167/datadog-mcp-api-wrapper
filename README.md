# Datadog MCP Server

A Model Context Protocol (MCP) server that enables LLMs to search and analyze Datadog logs and traces through natural language queries.

## Features

- **Log Search**: Search across all your Datadog logs with full query syntax support
- **Trace Search**: Query traces and spans to investigate application performance
- **Flexible Formatting**: Get results in human-readable Markdown or structured JSON
- **Smart Truncation**: Automatic response truncation with helpful guidance
- **Clear Error Handling**: Actionable error messages that guide you to solutions
- **Rate Limit Management**: Built-in retry logic and clear rate limit messages

## Prerequisites

- Python 3.10 or higher
- Poetry for dependency management
- A Datadog account with:
  - API Key
  - Application Key
  - Access to logs and/or traces

## Installation

1. Clone or download this repository:

```bash
cd datadog-mcp
```

2. Install dependencies using Poetry:

```bash
poetry install
```

## Configuration

### 1. Get Datadog API Credentials

You need three pieces of information from your Datadog account:

- **Datadog Site**: Your Datadog site URL (e.g., `datadoghq.com`, `datadoghq.eu`)
  - Find this in your Datadog URL: `https://app.datadoghq.com` → site is `datadoghq.com`

- **API Key**: Get from [API Keys settings](https://app.datadoghq.com/organization-settings/api-keys)
  - Click "New Key" if you need to create one
  - Copy the key value

- **Application Key**: Get from [Application Keys settings](https://app.datadoghq.com/organization-settings/application-keys)
  - Click "New Key" if you need to create one
  - Copy the key value

### 2. Set Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
DD_SITE=datadoghq.com
DD_API_KEY=your_actual_api_key_here
DD_APP_KEY=your_actual_app_key_here
```

Alternatively, export them in your shell:

```bash
export DD_SITE=datadoghq.com
export DD_API_KEY=your_actual_api_key_here
export DD_APP_KEY=your_actual_app_key_here
```

## Usage

### Running the Server

The MCP server runs as a long-lived process that communicates over stdio:

```bash
poetry run python -m datadog_mcp.server
```

The server will validate your configuration on startup and display any errors.

### Available Tools

#### 1. datadog_search_logs

Search for logs in Datadog.

**Parameters:**
- `query` (required): Search query using Datadog syntax
- `from_time` (optional): Start time (default: "now-15m")
- `to_time` (optional): End time (default: "now")
- `limit` (optional): Max results (default: 50, max: 1000)
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Examples:**

```python
# Search for errors in the last hour
{
  "query": "status:error",
  "from_time": "now-1h"
}

# Search specific service
{
  "query": "service:web-app AND @http.status_code:500",
  "from_time": "2024-01-01T00:00:00Z",
  "to_time": "2024-01-01T23:59:59Z"
}

# Get JSON output
{
  "query": "env:production error",
  "response_format": "json"
}
```

#### 2. datadog_search_traces

Search for traces and spans in Datadog.

**Parameters:**
- `query` (required): Search query using Datadog syntax
- `from_time` (optional): Start time (default: "now-15m")
- `to_time` (optional): End time (default: "now")
- `limit` (optional): Max results (default: 50, max: 1000)
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Examples:**

```python
# Find errors in a service
{
  "query": "service:web-app error:true",
  "from_time": "now-1h"
}

# Find slow API calls
{
  "query": "resource_name:GET /api/* @duration:>1000000000",
  "from_time": "now-30m"
}

# Get JSON output for analysis
{
  "query": "service:python*",
  "response_format": "json"
}
```

### Query Syntax

Both tools support the full Datadog query syntax:

**Basic Queries:**
- Simple text: `error`
- Field search: `service:web-app`
- Boolean operators: `service:web AND status:error`
- Wildcards: `service:python*`

**Facets:**
- HTTP status: `@http.status_code:500`
- Custom attributes: `@user.email:john@example.com`

**Tags:**
- Environment: `env:production`
- Multiple tags: `env:prod team:backend`

**Time Formats:**
- Date math: `now-15m`, `now-1h`, `now-1d`, `now-7d`
- ISO8601: `2024-01-01T00:00:00Z`
- Epoch milliseconds: `1704067200000`

**Learn More:**
- [Logs Query Syntax](https://docs.datadoghq.com/logs/explorer/search_syntax/)
- [Traces Query Syntax](https://docs.datadoghq.com/tracing/trace_explorer/query_syntax/)

## Integration with MCP Clients

### Claude Desktop

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "datadog": {
      "command": "poetry",
      "args": ["run", "python", "-m", "datadog_mcp.server"],
      "cwd": "/absolute/path/to/datadog-mcp",
      "env": {
        "DD_SITE": "datadoghq.com",
        "DD_API_KEY": "your_api_key",
        "DD_APP_KEY": "your_app_key"
      }
    }
  }
}
```

Replace `/absolute/path/to/datadog-mcp` with the actual path to this project.

### Other MCP Clients

The server uses stdio transport and follows the MCP protocol specification. Consult your MCP client documentation for integration instructions.

## Rate Limits

- **Logs API**: Generous rate limits (typically not an issue)
- **Traces API**: 300 requests per hour

If you hit rate limits, the server will return a clear error message with retry guidance.

## Troubleshooting

### Configuration Errors

**Error: Missing required environment variables**
- Ensure `DD_SITE`, `DD_API_KEY`, and `DD_APP_KEY` are set
- Check your `.env` file or environment variables
- Verify no typos in variable names

### Authentication Errors

**Error: Permission denied**
- Verify your API key and Application key are correct
- Ensure the keys have proper permissions for logs/traces
- Check if the keys have been rotated or expired
- Generate new keys if needed from Datadog settings

### Query Errors

**Error: Bad request**
- Check your query syntax
- Refer to Datadog query syntax documentation
- Try simplifying the query to isolate the issue
- Remove special characters that might need escaping

### Rate Limiting

**Error: Rate limit exceeded**
- Wait before making more requests (especially for traces: 300/hour)
- Use more specific queries to reduce request count
- Consider caching results on the client side
- Add longer time delays between requests

### Empty Results

If you're getting no results but expect some:
- Verify the time range with `from_time` and `to_time`
- Check that logs/traces exist for your query in Datadog UI
- Ensure you're searching the correct service names
- Try broader queries first, then narrow down

## Development

### Project Structure

```
datadog-mcp/
├── datadog_mcp/
│   ├── __init__.py       # Package initialization
│   ├── server.py         # Main MCP server with tool registrations
│   ├── config.py         # Configuration and environment validation
│   ├── models.py         # Pydantic input validation models
│   ├── client.py         # Datadog API client wrapper
│   ├── formatters.py     # Response formatting (Markdown/JSON)
│   └── errors.py         # Error handling utilities
├── pyproject.toml        # Poetry dependencies
├── README.md             # This file
└── .env.example          # Environment variable template
```

### Code Quality

The codebase follows these standards:
- Full type hints with Python type annotations
- Pydantic v2 for input validation
- Comprehensive docstrings (Sphinx-style)
- Async/await for all I/O operations
- DRY principle with shared utilities
- Clear error messages with actionable guidance

### Testing

To validate the implementation:

```bash
# Check Python syntax
poetry run python -m py_compile datadog_mcp/*.py

# Test server startup (will wait for requests)
poetry run python -m datadog_mcp.server
```

## License

This project is provided as-is for integration with Datadog services via the Model Context Protocol.

## Support

For issues related to:
- **MCP Protocol**: See [MCP Documentation](https://modelcontextprotocol.io)
- **Datadog API**: See [Datadog API Documentation](https://docs.datadoghq.com/api/)
- **This Server**: Open an issue in this repository

## Acknowledgments

Built with:
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Datadog API Client](https://github.com/DataDog/datadog-api-client-python)
- [Pydantic](https://docs.pydantic.dev/)
