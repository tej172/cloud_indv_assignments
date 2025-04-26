# Chapter 6: Transports - The Delivery Service

In the last chapter, [FastMCP Server](05_fastmcp_server.md), we learned how to build our own MCP server assistant using the `FastMCP` framework. We saw how easy it is to define tools and have `FastMCP` handle the MCP protocol details.

But we skipped over a crucial detail: how does our client code, using the `ClientSession` from [Chapter 1: Client Session](01_client_session.md), actually *talk* to the server we built? They might be running on the same computer, or maybe the server is on a different machine across the internet. How do the request and response messages physically travel between them?

This is where **Transports** come in!

## Motivation: Choosing Your Delivery Method

Imagine you wrote a letter (an MCP request message, like asking to call a tool). You need to send it to your friend (the MCP server). How do you get it there?

*   You could hand it directly to them if they're right next to you (like a local program).
*   You could use the postal service (like standard input/output for local programs).
*   You could use a special courier service that provides continuous updates (like Server-Sent Events over the web).
*   You could establish a direct, instant phone line (like WebSockets).

Each method gets the letter delivered, but they work differently and are suited for different situations.

In the world of `python-sdk` and MCP, the **Transport** is the underlying communication mechanism chosen to send messages between the client and the server. It's the actual delivery service used for the MCP messages formatted by `ClientSession` and understood by the server.

## What is a Transport?

A **Transport** handles the low-level details of setting up a connection and sending/receiving the actual bytes that make up the MCP messages. Think of it as the plumbing that connects the client and the server.

The `ClientSession` we learned about in [Chapter 1: Client Session](01_client_session.md) is responsible for *formatting* the messages (like `tools/list` requests) and *interpreting* the replies. But it relies on a Transport to do the actual sending and receiving over the chosen communication channel.

The `python-sdk` provides built-in support for several common transports:

1.  **Standard Input/Output (Stdio):**
    *   **Analogy:** Sending letters via postal mail to a local address, or talking to a command-line tool.
    *   **How it works:** The client starts the server as a local process (like running a command in your terminal). The client sends messages to the server's standard input ("stdin") and reads responses from the server's standard output ("stdout").
    *   **Use Case:** Perfect when the client application needs to start and manage a local MCP server process running on the same machine. This is what we implicitly used in Chapter 1 and Chapter 5!

2.  **Server-Sent Events (SSE over HTTP):**
    *   **Analogy:** A continuous news ticker feed delivered over the web.
    *   **How it works:** The client connects to a specific web URL on the server using standard HTTP. The server can then *push* messages (events) to the client over this connection whenever it wants. To send messages *to* the server, the client typically makes separate standard HTTP POST requests to another URL defined by the server.
    *   **Use Case:** Good for web-based scenarios where the server needs to proactively send updates or notifications to the client (like progress updates, new messages).

3.  **WebSockets:**
    *   **Analogy:** A direct, two-way phone line established over the web.
    *   **How it works:** The client and server establish a persistent, full-duplex (two-way) connection. Both the client and server can send messages to each other at any time over this single connection once it's established.
    *   **Use Case:** Ideal for real-time, interactive applications requiring low-latency communication in both directions (e.g., chat applications, live dashboards, collaborative tools).

## Using Transports with `ClientSession`

The beauty is that `ClientSession` itself doesn't need to know the complex details of *how* stdio, SSE, or WebSockets work. It just needs two things:

*   A way to **read** incoming messages (`read_stream`).
*   A way to **write** outgoing messages (`write_stream`).

The `python-sdk` provides helper functions (like `stdio_client`, `sse_client`, `websocket_client`) that set up the specific transport mechanism and give you back these two streams. You then pass these streams to `ClientSession`.

Let's see how you'd use each transport helper.

**1. Stdio Transport**

This is the one we saw in [Chapter 1: Client Session](01_client_session.md). We define how to run the server command and then use `stdio_client`.

```python
# Using stdio transport (like in Chapter 1)
import asyncio
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client # <-- Stdio helper

logging.basicConfig(level=logging.INFO)

async def connect_via_stdio(server_command: str):
    server_params = StdioServerParameters(command=server_command)

    # stdio_client starts the process and provides streams
    async with stdio_client(server_params) as (read_stream, write_stream):
        logging.info("Stdio transport connected.")
        # ClientSession uses the streams from stdio_client
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            logging.info("Session initialized via stdio.")
            # ... use session.list_tools(), session.call_tool(), etc. ...
            tools = await session.list_tools()
            logging.info(f"Tools via stdio: {tools}")

# Example: asyncio.run(connect_via_stdio("python your_server_script.py"))
```

*   `StdioServerParameters` tells `stdio_client` *how* to run the server process.
*   `stdio_client(...)` starts the server process and yields the `read_stream` (connected to server's stdout) and `write_stream` (connected to server's stdin).
*   `ClientSession(read_stream, write_stream)` uses these streams to communicate.

**2. SSE Transport**

To connect to an MCP server running with an SSE endpoint (e.g., hosted by a web server), you use `sse_client`.

```python
# Using SSE transport
import asyncio
import logging
from mcp import ClientSession
from mcp.client.sse import sse_client # <-- SSE helper

logging.basicConfig(level=logging.INFO)

async def connect_via_sse(server_sse_url: str):
    # sse_client connects to the URL and provides streams
    # It handles the SSE event listening and POSTing for sending
    async with sse_client(server_sse_url) as (read_stream, write_stream):
        logging.info("SSE transport connected.")
        # ClientSession uses the streams from sse_client
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            logging.info("Session initialized via SSE.")
            # ... use session methods ...
            tools = await session.list_tools()
            logging.info(f"Tools via SSE: {tools}")

# Example: asyncio.run(connect_via_sse("http://localhost:8000/sse"))
```

*   `sse_client(server_sse_url)` connects to the specified HTTP endpoint, sets up the SSE listener for incoming messages (`read_stream`), and prepares to send outgoing messages via HTTP POST (`write_stream`).
*   `ClientSession` uses these streams, unaware of the underlying HTTP/SSE mechanics.

**3. WebSocket Transport**

To connect to an MCP server using a WebSocket endpoint, you use `websocket_client`.

```python
# Using WebSocket transport
import asyncio
import logging
from mcp import ClientSession
from mcp.client.websocket import websocket_client # <-- WebSocket helper

logging.basicConfig(level=logging.INFO)

async def connect_via_websocket(server_ws_url: str):
    # websocket_client establishes the WebSocket connection
    async with websocket_client(server_ws_url) as (read_stream, write_stream):
        logging.info("WebSocket transport connected.")
        # ClientSession uses the streams from websocket_client
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            logging.info("Session initialized via WebSocket.")
            # ... use session methods ...
            tools = await session.list_tools()
            logging.info(f"Tools via WebSocket: {tools}")

# Example: asyncio.run(connect_via_websocket("ws://localhost:8000/ws"))
```

*   `websocket_client(server_ws_url)` connects to the WebSocket URL (`ws://...` or `wss://...`) and yields streams representing the bidirectional connection.
*   `ClientSession` uses these streams to send and receive MCP messages over the WebSocket.

Notice the pattern: You choose the appropriate `*_client` helper based on how the server is exposed, but the way you create and use `ClientSession` remains the same!

```python
# General Pattern
# 1. Choose and configure the transport helper
# async with stdio_client(...) as (read_stream, write_stream):
# async with sse_client(...) as (read_stream, write_stream):
# async with websocket_client(...) as (read_stream, write_stream):

# 2. Pass the provided streams to ClientSession
#     async with ClientSession(read_stream, write_stream) as session:
#         # 3. Initialize and use the session as usual
#         await session.initialize()
#         result = await session.list_tools()
#         # ...
```

## Under the Hood: How Transports Provide Streams

How do these `*_client` functions hide the complexity? They act as adapters.

1.  **Connection:** Each helper establishes the specific type of connection (starts a process, makes HTTP requests, opens a WebSocket).
2.  **Internal Queues:** They typically use internal memory queues or buffers (often using `anyio.create_memory_object_stream`).
3.  **Reading:** They run background tasks that continuously read raw data from the connection (process stdout, SSE events, WebSocket frames), parse it into MCP messages (or detect errors), and put these messages/errors onto the internal *read* queue. The `read_stream` you get simply reads from this queue.
4.  **Writing:** When you send a message to the `write_stream`, it goes into an internal *write* queue. Another background task reads from this queue, formats the message according to the transport's protocol (e.g., adds newline for stdio, makes HTTP POST for SSE, sends WebSocket frame), and sends it over the actual connection.

This setup decouples `ClientSession` from the specific transport details. `ClientSession` just interacts with the clean `read_stream` and `write_stream` interfaces.

```mermaid
graph LR
    subgraph Your Code
        A[ClientSession]
    end
    subgraph Transport Helper (e.g., stdio_client)
        direction LR
        B[read_stream] -- Reads From --> C(Internal Read Queue)
        D(Internal Write Queue) -- Writes To --> E[write_stream]
        F[Background Reader Task] -- Writes To --> C
        G[Background Writer Task] -- Reads From --> D
    end
    subgraph Actual Connection
        H[Process Pipes / HTTP / WebSocket]
    end
    subgraph Server
        I[MCP Server]
    end

    A -- Uses --> B
    A -- Uses --> E

    F -- Reads From --> H
    G -- Writes To --> H
    H -- Communicates With --> I
```

The `Transport Helper` box manages the `Internal Queues` and `Background Tasks` to bridge the gap between the `Actual Connection` and the simple `read_stream`/`write_stream` used by `ClientSession`.

You can explore the implementation details in the `mcp.client` subdirectories:
*   `src/mcp/client/stdio/`: Code for starting processes and managing stdin/stdout.
*   `src/mcp/client/sse.py`: Code for handling SSE connections and HTTP POST requests.
*   `src/mcp/client/websocket.py`: Code for managing WebSocket communication.

Similarly, the `mcp.server` directory contains corresponding transport implementations for the server side (e.g., `src/mcp/server/stdio.py`, `src/mcp/server/sse.py`, `src/mcp/server/websocket.py`) that frameworks like [FastMCP Server](05_fastmcp_server.md) can use.

## Conclusion

In this chapter, we peeled back a layer to understand **Transports** – the delivery mechanisms that connect MCP clients and servers.

*   Transports handle the low-level communication (stdio, SSE, WebSocket).
*   They provide simple `read_stream` and `write_stream` interfaces for `ClientSession`.
*   Helper functions (`stdio_client`, `sse_client`, `websocket_client`) manage the specifics of each transport type.
*   You choose the transport based on how your client needs to connect to the server.

Understanding transports gives you flexibility in how you deploy and connect your MCP applications.

Now that we've covered the core components – sessions, tools, resources, prompts, servers, and transports – let's look at a more advanced server concept: how servers built with `FastMCP` can maintain state and context across multiple requests within a single client session. We'll explore this in the next chapter: [FastMCP Context](07_fastmcp_context.md).

---

Generated by [Github LLM Codebase Knowledge Building Summarizer using Openai/Gemini/Claud](https://github.com/tej172/cloud_indv_assignments/tree/main/ass_2)