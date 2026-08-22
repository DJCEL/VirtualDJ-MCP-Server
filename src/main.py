import sys
import asyncio

from rich.console import Console
console = Console(file=sys.stderr)

from virtualdj_client import VirtualDJClient
from virtualdj_mcp_server import run_mcp_server

#------------------------------------------------------------------------------------------------------------------------------------
def main():

    # Initialize VirtualDJ client
    vdj_client = VirtualDJClient()

    vdj_client_connected = False
    vdj_client_connected = asyncio.run(vdj_client.is_running())
    console.print(f"VirtualDJ connected: {vdj_client_connected}")
    if (vdj_client_connected == False):
        sys.exit()


    # Run the FastMCP server
    try:
        run_mcp_server(vdj_client)
    except KeyboardInterrupt:
        console.print("Server shutdown requested")
    except Exception as e:
        console.print(f"Server error: {e}")
        raise
    finally:
        console.print("VirtualDJ-MCP Server stopped")
#------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
