# HTTP Transport with Streamable HTTP

The MCP server now supports Streamable HTTP transport in addition to stdio. This allows you to run the server over HTTP, making it accessible via web requests and enabling integration with web applications.

## Overview

Streamable HTTP is the recommended transport for production deployments of MCP servers. It provides:

- **Stateless or stateful operation**: Choose between session-based or completely stateless requests
- **JSON or SSE responses**: Return either JSON responses or Server-Sent Events (SSE) streams
- **Bi-directional communication**: Supports both client-to-server and server-to-client messages
- **Scalability**: Works well with load balancers and horizontal scaling

## Configuration

Add these settings to your `.env` file:

```env
# Transport mode: stdio, http, or both
MCP_TRANSPORT=http

# HTTP server settings
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8080

# HTTP transport options
MCP_HTTP_JSON_RESPONSE=false  # Use SSE streams (default) or JSON responses
MCP_HTTP_STATELESS=false      # Enable stateless mode (no session tracking)
```

### Transport Modes

- **`stdio`**: Traditional stdio transport (default) - suitable for local CLI usage
- **`http`**: HTTP with Streamable HTTP transport - suitable for web applications
- **`both`**: Run both transports simultaneously - useful during migration

### HTTP Options

#### JSON Response Mode (`MCP_HTTP_JSON_RESPONSE`)

- **`false`** (default): Returns Server-Sent Events (SSE) streams
  - Better for real-time updates
  - Maintains persistent connections
  - Ideal for streaming responses

- **`true`**: Returns standard JSON responses
  - Simpler to integrate with REST clients
  - Each request is independent
  - Better for simple request-response patterns

#### Stateless Mode (`MCP_HTTP_STATELESS`)

- **`false`** (default): Session-based mode
  - Maintains session state across requests
  - Supports resumable connections
  - Better user experience with connection recovery

- **`true`**: Stateless mode
  - Creates fresh transport for each request
  - No session tracking or state persistence
  - Better for horizontal scaling and load balancing

## Running the Server

### HTTP Only

```bash
# Set transport to HTTP in .env
MCP_TRANSPORT=http

# Start the server
python -m src.server
```

The server will start on `http://0.0.0.0:8080` with the MCP endpoint at `/mcp`.

### Both Stdio and HTTP

```bash
# Set transport to both
MCP_TRANSPORT=both

# Start the server
python -m src.server
```

This runs both transports concurrently, allowing clients to connect via either stdio or HTTP.

## Endpoints

### `/mcp` - MCP Protocol Endpoint

The main endpoint for MCP communication.

**Methods**: `GET`, `POST`

**Headers**:
- `MCP-Session-ID`: Optional session identifier (for session-based mode)
- `Last-Event-ID`: For resuming SSE streams (when resumability is enabled)

**Request/Response Format**:
- SSE mode: Returns `text/event-stream` with Server-Sent Events
- JSON mode: Returns `application/json` with standard JSON-RPC responses

### `/health` - Health Check Endpoint

Simple health check endpoint.

**Method**: `GET`

**Response**:
```json
{"status": "healthy"}
```

## Client Integration

### Using with Web Applications

```javascript
// Connect to MCP server via HTTP
const response = await fetch('http://localhost:8080/mcp', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/list',
    params: {}
  })
});

const data = await response.json();
console.log(data);
```

### Using with SSE (Server-Sent Events)

```javascript
// Connect to MCP server via SSE
const eventSource = new EventSource('http://localhost:8080/mcp');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
};
```

### Using with Open WebUI

Configure Open WebUI to connect to the HTTP endpoint:

```bash
# In Open WebUI settings, add MCP server
Server URL: http://localhost:8080/mcp
```

## Production Deployment

### Recommended Settings

For production deployments:

```env
MCP_TRANSPORT=http
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8080
MCP_HTTP_JSON_RESPONSE=true  # Simpler for most clients
MCP_HTTP_STATELESS=true      # Better for scaling
LOG_LEVEL=WARNING
```

### With Reverse Proxy (nginx)

```nginx
upstream mcp_server {
    server localhost:8080;
}

server {
    listen 80;
    server_name your-domain.com;

    location /mcp {
        proxy_pass http://mcp_server;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # For SSE support
        proxy_buffering off;
        proxy_cache off;
    }
}
```

### With Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

ENV MCP_TRANSPORT=http
ENV MCP_SERVER_HOST=0.0.0.0
ENV MCP_SERVER_PORT=8080

EXPOSE 8080

CMD ["python", "-m", "src.server"]
```

## Security Considerations

1. **Network Exposure**: HTTP transport exposes the server to network requests
   - Use firewall rules to restrict access
   - Consider using a reverse proxy with authentication
   - Enable HTTPS/TLS in production

2. **Authentication**: The current implementation doesn't include authentication
   - Add authentication middleware if needed
   - Use API keys or OAuth tokens
   - Consider integration with existing auth systems

3. **Rate Limiting**: Consider adding rate limiting for HTTP endpoints
   - Prevents abuse and DoS attacks
   - Can be implemented at the application or reverse proxy level

4. **CORS**: If accessing from browsers, configure CORS headers appropriately

## Troubleshooting

### Server Won't Start

Check if the port is already in use:
```bash
lsof -i :8080
```

Try a different port:
```env
MCP_SERVER_PORT=8081
```

### Connection Refused

Verify the server is running:
```bash
curl http://localhost:8080/health
```

Check firewall settings:
```bash
# macOS
sudo pfctl -s rules

# Linux
sudo iptables -L
```

### SSE Connection Issues

Ensure proxy/load balancer supports SSE:
- Disable buffering
- Support HTTP/1.1 chunked encoding
- Keep connections open

## Performance Tuning

### For High Traffic

```env
# Use stateless mode for better scaling
MCP_HTTP_STATELESS=true

# Use JSON responses for simplicity
MCP_HTTP_JSON_RESPONSE=true

# Adjust uvicorn workers
# Run with: uvicorn --workers 4 --host 0.0.0.0 --port 8080
```

### For Real-Time Applications

```env
# Use session-based mode for better UX
MCP_HTTP_STATELESS=false

# Use SSE for real-time updates
MCP_HTTP_JSON_RESPONSE=false
```

## References

- [MCP Streamable HTTP Specification](https://modelcontextprotocol.io/)
- [Cloudflare Blog: Streamable HTTP Transport](https://blog.cloudflare.com/streamable-http-mcp-servers-python/)
- [MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [Starlette Documentation](https://www.starlette.io/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
