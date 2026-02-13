# Rasdaman MCP Server

This tool enables users to interact with rasdaman in a natural language context.
By exposing rasdaman functionality as tools via the MCP protocol, an LLM can query the database to answer questions like:

- "What datacubes are available?"
- "What are the dimensions of the 'Sentinel2_10m' coverage?"
- "Create an NDVI image for June 12, 2025."

The MCP server translates these tool calls into actual WCS/WCPS queries that rasdaman can understand and then returns the results to the LLM.

## Installation

```bash
pip install rasdaman-mcp
```

## Usage

First the connection from the MCP server to rasdaman needs to be configured, either through environment variables:

 - `RASDAMAN_URL`: URL for the rasdaman server
 - `RASDAMAN_USERNAME`: Username for authentication
 - `RASDAMAN_PASSWORD`: Password for authentication

or command-line arguments to the `rasdaman-mcp` tool:

 - `--rasdaman-url`: URL for the rasdaman server (default `RASDAMAN_URL` env variable or `http://localhost:8080/rasdaman/ows`).
 - `--username`: Username for authentication (default `RASDAMAN_USERNAME` env variable or `rasguest`).
 - `--password`: Sets the password for authentication (default `RASDAMAN_PASSWORD` env variable or `rasguest`).

Then the MCP is ready to be used with an AI agent tool, in one of two modes: `stdio` (default) or `http`.

### `stdio` Mode
Used for direct integration with clients that take over managing the server process and communicate with it through standard input/output.
Generally in your AI tool you need to specify the command to run `rasdaman-mcp`:

    rasdaman-mcp --username rasguest --password rasguest --rasdaman-url "..."

Example for enabling it in gemini-cli:

    gemini mcp add rasdaman-mcp "rasdaman-mcp --username rasguest --password rasguest"

Benefits:
- Simplicity: No need to manage a separate server process or ports.
- Seamless Integration: Tools are transparently made available to the LLM within the client environment.

### `http` Mode
This mode starts a standalone Web server listening on a specified host/port, e.g:

    rasdaman-mcp --transport http --host 127.0.0.1 --port 8000 --rasdaman-url "..."

The MCP server URL to be configured in your AI agent would be `http://127.0.0.1:8000/mcp` with transport `streamable-http`.
For example, for Mistral Vibe extend the config.toml with a section like this:

    [[mcp_servers]]
    name = "rasdaman-mcp"
    transport = "streamable-http"
    url = "http://127.0.0.1:8000/mcp/"

Benefits:
- Scalability: The MCP server can be containerized (e.g., with Docker) and deployed as a separate microservice.
- Decoupling: Any client that can speak HTTP (e.g., `curl`, Python scripts, web apps, other LLM clients) can interact with the tools.
- Testing: Allows for direct API testing and debugging, independent of an LLM client.

### AI agents

Once an AI agent is configured with access to `rasdaman-mcp`, it becomes capable of using several tools:

- list coverages in the configured rasdaman
- get the details of a particular coverage
- execute processing/analytics queries based on a description in natural language



## Examples

The following examples demonstrate the interaction with an AI agent using the rasdaman MCP server.

### Listing Coverages

![](https://github.com/rasdaman/rasdaman-mcp/blob/main/docs/assets/img/01-list_coverages.png?raw=true)

### Describing a Coverage

![](https://github.com/rasdaman/rasdaman-mcp/blob/main/docs/assets/img/02-describe-coverage.png?raw=true)

### Executing a Query

![](https://github.com/rasdaman/rasdaman-mcp/blob/main/docs/assets/img/03-execute-query.png?raw=true)

### Query Result Visualization

![](https://github.com/rasdaman/rasdaman-mcp/blob/main/docs/assets/img/03.1-stretched_era5_scaled.png?raw=true)

### Natural Language Query Suggestion

![](https://github.com/rasdaman/rasdaman-mcp/blob/main/docs/assets/img/04-suggest-query.png?raw=true)

## Development

### Setup

1. Clone the [git repository](https://github.com/rasdaman/rasdaman-mcp):
   ```bash
   git clone https://github.com/rasdaman/rasdaman-mcp.git
   cd rasdaman-mcp/
   ```

2. Create a virtual environment (if you don't have one):
   ```bash
   uv venv
   ```

3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

4. Install from source:
   ```bash
   uv pip install -e .
   ```

### Core Components

- Main Application (`main.py`): This script initializes the FastMCP application. It handles command-line arguments for transport selection, rasdaman URL,
  username, and password. It then instantiates the `RasdamanActions` class and decorates its methods to expose them as tools.
- `RasdamanActions` Class (`rasdaman_actions.py`): Encapsulates all interaction with the rasdaman WCS/WCPS endpoints.
  It is initialized with the server URL and credentials, and its methods contain the logic for listing coverages, describing them, and executing queries.
- WCPS crash course (`wcps_crash_course.py`): A short summary of the syntax of WCPS, allowing LLMs to generate more accurate queries.

### Defined Tools

The following methods are exposed as tools:
- `list_coverages()`: Lists all available datacubes.
- `describe_coverage(coverage_id)`: Retrieves metadata for a specific datacube.
- `wcps_query_crash_course()`: Returns a crash course on WCPS syntax with examples and best practices.
- `execute_wcps_query(wcps_query)`: Executes a raw WCPS query and returns a result either directly as a string (scalars or small json), or as a filepath.

### Documentation

To build the documentation:

```bash
# install dependencies
uv pip install '.[docs]'

sphinx-build docs docs/_build
```

You can then open `docs/_build/index.html` in the browser.

### Automated Tests

To run the tests:

```bash
# install dependencies
uv pip install '.[tests]'

pytest
```


### Manual Testing

Interacting with the standalone HTTP server *manually* requires a specific 3-step process using `curl`.
The `fastmcp` protocol is stateful and requires a session to be explicitly initialized.

1. First, send an `initialize` request. This will return a `200 OK` response and, most importantly, 
   a session ID in the `mcp-session-id` response header (needed in the next steps).

    ```bash
    curl -i -X POST \
    -H "Accept: text/event-stream, application/json" \
    -H "Content-Type: application/json" \
    -d '{
          "jsonrpc": "2.0",
          "method": "initialize",
          "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": { "name": "curl-client", "version": "1.0.0" }
          },
          "id": 1
        }' \
    "http://127.0.0.1:8000/mcp"
    ```

2. Next, send a notification to the server to confirm the session is ready. Use the session ID from Step 1 in the `mcp-session-id` header. 
   This request will not produce a body in the response.

    ```bash
    SESSION_ID="<YOUR_SESSION_ID>"
    
    curl -X POST \
    -H "Accept: text/event-stream, application/json" \
    -H "Content-Type: application/json" \
    -H "Mcp-Session-Id: $SESSION_ID" \
    -d '{
          "jsonrpc": "2.0",
          "method": "notifications/initialized"
        }' \
    "http://127.0.0.1:8000/mcp"
    ```

3. Finally, you can call a tool using the `tools/call` method. The `params` object must contain the `name` of the tool and 
   an `arguments` object with the parameters for that tool. The server will respond with the result of the tool call in a JSON-RPC response.
    
    ```bash
    SESSION_ID="<YOUR_SESSION_ID>"
    
    # Example: Calling the 'list_coverages' tool
    curl -X POST \
    -H "Accept: text/event-stream, application/json" \
    -H "Content-Type: application/json" \
    -H "Mcp-Session-Id: $SESSION_ID" \
    -d '{
          "jsonrpc": "2.0",
          "method": "tools/call",
          "params": {
            "name": "list_coverages",
            "arguments": {}
          },
          "id": 2
        }' \
    "http://127.0.0.1:8000/mcp"
    ```
