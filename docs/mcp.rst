===========
MCP Servers
===========

``pyngrok`` can make a `Model Context Protocol <https://modelcontextprotocol.io>`_ (MCP) server running on your machine
available to remote MCP clients (for instance, cloud AI assistants) by tunneling to its Streamable HTTP transport. The
examples below use the `MCP Python SDK <https://github.com/modelcontextprotocol/python-sdk>`_.

Be sure to secure your server before opening a tunnel to it. Anyone with your tunnel's URL can reach the server, and MCP
tools often act on your machine or your data, which is why every example here requires authentication. MCP clients call
tools based on what the AI model reads, so only expose the tools a remote client needs. And if a server holds personal
credentials (a login to one of your accounts, for instance), you may want to keep it on your machine with the ``stdio``
transport instead. See the
`MCP security best practices <https://modelcontextprotocol.io/specification/latest/basic/security_best_practices>`_ for
more.

Quick Start
-----------

This example requires a bearer token on every request. The server checks the token itself, so it never leaves your
machine, and requests made directly to ``localhost`` need it too. Since the SDK rejects requests that aren't addressed
to ``localhost``, the tunnel also rewrites the ``Host`` header. Create ``server.py`` with the following code:

.. code-block:: python

    import hmac
    import os

    import uvicorn
    from mcp.server.mcpserver import MCPServer
    from pyngrok import ngrok
    from starlette.responses import PlainTextResponse

    port = os.environ.get("PORT", "8000")
    token = os.environ.get("MCP_TOKEN")
    if not token:
        raise SystemExit("Set MCP_TOKEN to a random secret")

    mcp = MCPServer("demo")

    @mcp.tool()
    def add(a: int, b: int) -> int:
        return a + b

    # ... Implement the rest of your MCP tools

    class RequireBearerToken:
        def __init__(self, app, token):
            self.app = app
            self.expected = f"Bearer {token}".encode()

        async def __call__(self, scope, receive, send):
            if scope["type"] == "http":
                authorization = dict(scope["headers"]).get(b"authorization", b"")
                if not hmac.compare_digest(authorization, self.expected):
                    await PlainTextResponse("Unauthorized", status_code=401)(scope, receive, send)
                    return
            await self.app(scope, receive, send)

    # Rewrite the Host header to localhost on requests to the tunnel
    traffic_policy = {
        "on_http_request": [{
            "actions": [{"type": "add-headers", "config": {"headers": {"host": f"localhost:{port}"}}}]
        }]
    }

    # Open a ngrok tunnel to the MCP server
    public_url = ngrok.connect(port, traffic_policy=traffic_policy).public_url
    print(f"MCP server URL: {public_url}/mcp")
    print("Configure your MCP client to send the header: Authorization: Bearer <MCP_TOKEN>")

    # Start the MCP server, requiring the bearer token on every request
    uvicorn.run(RequireBearerToken(mcp.streamable_http_app(), token), host="127.0.0.1", port=int(port))

Next, generate a random token and start the server. If ``MCP_TOKEN`` isn't set (or is empty), the server won't start.

.. code-block:: sh

    export MCP_TOKEN=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
    NGROK_AUTHTOKEN=$NGROK_AUTHTOKEN python server.py

That's it! MCP clients that let you configure custom headers can now connect to ``<public_url>/mcp``, sending the
header ``Authorization: Bearer <MCP_TOKEN>``. If you're using ``mcp`` 1.x, use ``FastMCP`` (from ``mcp.server.fastmcp``)
instead, and pass any transport settings (like ``streamable_http_path``) to its constructor.

Clients That Can't Send Headers
-------------------------------

Some MCP clients only let you enter a URL, with no way to set a header. For those, you can serve the MCP server at a
secret path instead. Create ``server.py`` with the following code:

.. code-block:: python

    import os

    from mcp.server.mcpserver import MCPServer
    from pyngrok import ngrok

    port = os.environ.get("PORT", "8000")
    secret = os.environ.get("MCP_SECRET")
    if not secret:
        raise SystemExit("Set MCP_SECRET to a random secret")
    mcp_path = f"/{secret}/mcp"

    mcp = MCPServer("demo")

    @mcp.tool()
    def add(a: int, b: int) -> int:
        return a + b

    # ... Implement the rest of your MCP tools

    # Rewrite the Host header to localhost on requests to the tunnel
    traffic_policy = {
        "on_http_request": [{
            "actions": [{"type": "add-headers", "config": {"headers": {"host": f"localhost:{port}"}}}]
        }]
    }

    # Open a ngrok tunnel to the MCP server
    public_url = ngrok.connect(port, traffic_policy=traffic_policy).public_url
    print(f"MCP server URL: {public_url}{mcp_path}")

    # Start the MCP server, serving it only at the secret path
    mcp.run(transport="streamable-http", port=int(port), streamable_http_path=mcp_path)

Generate ``MCP_SECRET`` the same way as ``MCP_TOKEN`` above. Keep in mind that a secret path is only a shared secret.
Anyone who has the URL can call the server, and URLs tend to leak more easily than headers do (through logs or browser
history, for instance). If the secret leaks, rotate it, and don't use this approach for servers that access sensitive
data.

OAuth
-----

If your server accesses sensitive data, it should implement OAuth as described in the
`MCP authorization spec <https://modelcontextprotocol.io/specification/latest/basic/authorization>`_. MCP clients that
support it will run the sign-in flow when your server asks for it, and ``ngrok`` forwards those requests to your server
like any other. The `MCP Python SDK <https://github.com/modelcontextprotocol/python-sdk>`_ can act as the OAuth resource
server for this.

Restrict by IP
--------------

For an extra layer of protection, ``ngrok`` can limit requests to the IP ranges of known services. For example, to only
allow requests from Anthropic's API servers, add this rule to the start of ``on_http_request`` in either example above:

.. code-block:: python

    {
        "expressions": ["!('com.anthropic.api' in conn.client_ip.categories)"],
        "actions": [{"type": "deny", "config": {"status_code": 403}}]
    }

Since this doesn't tell you which user is calling, use it alongside a token or secret rather than on its own. It will
also reject clients running on your own machine. See
`ngrok's MCP guide <https://ngrok.com/docs/gateway/api-gateway/mcp-gateway>`_ for other IP categories and more ways to
protect your server.

Troubleshooting
---------------

- If the server exits with ``Set MCP_TOKEN to a random secret`` (or ``MCP_SECRET``), set the environment variable to a
  generated value before running the script.
- A ``401 Unauthorized`` means the client either isn't sending ``Authorization: Bearer <MCP_TOKEN>`` or is sending the
  wrong token.
- A ``404 Not Found`` means the client's URL is missing the full path, ``/mcp`` (or ``/<MCP_SECRET>/mcp``).
- A ``421 Misdirected Request`` means the request reached the server without its ``Host`` header rewritten to
  ``localhost``, so check that the ``add-headers`` action is in your Traffic Policy.
