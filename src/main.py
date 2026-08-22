import sys
from fastmcp import FastMCP
from rich.console import Console

console = Console(file=sys.stderr)

from starlette.requests import Request
from starlette.responses import PlainTextResponse

from .config import MCP_SERVER_TRANSPORT, MCP_SERVER_HTTP, MCP_SERVER_PORT, MCP_SERVER_DEFAULT_PATH

#------------------------------------------------------------------------------------------------------------------------------------
def define_mcp_server_api_routes(mcp: FastMCP):

    @mcp.custom_route("/", methods=["GET"])
    async def api_root(request: Request) -> PlainTextResponse:
        result = PlainTextResponse("VirtualDJ-MCP-Server")
        return result

    @mcp.custom_route("/api", methods=["GET"])
    async def api_index():
        result = {
            "service": "virtualdj-mcp",
            "version": "1.0.0",
            "endpoints": {
                "health": "/api/health",
                "settings": "/api/settings",
                "deck_status": "/api/v1/deck/{deck_id}/status",
                "deck_load": "/api/v1/deck/{deck_id}/load",
                "deck_play_pause": "/api/v1/deck/{deck_id}/play_pause",
                "deck_sync": "/api/v1/deck/{deck_id}/sync",
                "deck_cue": "/api/v1/deck/{deck_id}/cue",
            },
        }
        return result
#------------------------------------------------------------------------------------------------------------------------------------
def define_mcp_server_api_tools(mcp: FastMCP):
    @mcp.tool(
        name="greet",
        description="Greet a user by name.")
    def greet(name: str) -> str:
        """Greet a user by name."""
        return f"Hello, {name}!"

    @mcp.tool
    def multiply(a: float, b: float) -> float:
        """Multiplies two numbers together."""
        return a * b
#------------------------------------------------------------------------------------------------------------------------------------
def define_mcp_server_api_resources(mcp: FastMCP):
    @mcp.resource("resource://greeting")
    def get_greeting() -> str:
        """Provides a simple greeting message."""
        return "Hello from FastMCP Resources!"

    @mcp.resource(
        uri="data://app-status",
        mime_type="application/json",
        description="Provides the current status of the application.")
    def get_application_status() -> str:
        """Provides the current status of the application."""
        import json
        result = json.dumps({"status": "ok", "uptime": 12345, "version": "2.1"})
        return result

    @mcp.resource("file:///app/data/important_log.txt", mime_type="text/plain")
    async def read_important_log() -> str:
        """Reads content from a specific log file asynchronously."""
        import aiofiles
        try:
            async with aiofiles.open("/app/data/important_log.txt", mode="r") as f:
                content = await f.read()
            return content
        except FileNotFoundError:
            return "Log file not found."
#------------------------------------------------------------------------------------------------------------------------------------
def define_mcp_server_api_prompts(mcp: FastMCP):
    @mcp.prompt
    def ask_about_topic(topic: str) -> str:
        """Generates a user message asking for an explanation of a topic."""
        return f"Can you please explain the concept of '{topic}'?"
#------------------------------------------------------------------------------------------------------------------------------------
def define_mcp_server_api(mcp: FastMCP):
    #define_mcp_server_api_tools(mcp)
    #define_mcp_server_api_resources(mcp)
    #define_mcp_server_api_prompts(mcp)
    define_mcp_server_api_routes(mcp) 
#------------------------------------------------------------------------------------------------------------------------------------
def create_mcp_server():
    mcp = FastMCP("VirtualDJ-MCP",
                  instructions="Provides an API to communicate with VirtualDJ.",
                  on_duplicate="warn")

    define_mcp_server_api(mcp)

    if MCP_SERVER_TRANSPORT == "stdio":
        mcp.run()
    elif MCP_SERVER_TRANSPORT == "http":
        mcp.run(transport=MCP_SERVER_TRANSPORT.lower(), host=MCP_SERVER_HOST, port=MCP_SERVER_PORT, path=MCP_SERVER_DEFAULT_PATH)
    else:
        console.print(f"[red]MCP_SERVER_TRANSPORT error.[/red]")
 
    return mcp
#------------------------------------------------------------------------------------------------------------------------------------
def main():
    console.print("[green]VirtualDJ-MCP-Server starting...[/green]")

    try:
        mcp = create_mcp_server()
    except KeyboardInterrupt:
        console.print("[yellow]MCP Server shutdown requested[/yellow]")
    except Exception as e:
        console.print(f"[red]MCP Server error: {e}[/red]")
        raise
    finally:
        console.print("[green]VirtualDJ-MCP MCP Server stopped[/green]")
#------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
