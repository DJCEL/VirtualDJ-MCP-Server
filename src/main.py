import sys
from rich.console import Console

from virtualdj_mcp_server import run_mcp_server

#------------------------------------------------------------------------------------------------------------------------------------
def main():
    console = Console(file=sys.stderr)

    # Run the FastMCP server
    try:
        run_mcp_server()
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
