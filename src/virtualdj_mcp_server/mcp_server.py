from fastmcp import FastMCP
from fastmcp.tools import tool
from rich.console import Console
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from .mcp_server_config import MCP_SERVER_TRANSPORT, MCP_SERVER_HOST, MCP_SERVER_PORT, MCP_SERVER_DEFAULT_PATH
from .virtualdj_client import VirtualDJClient

console = Console()


#------------------------------------------------------------------------------------------------------------------------------------
class VirtualDJMCPServer:
    def __init__(self):
        self.vdj_client = VirtualDJClient()
        self._create_mcp_server()
    #------------------------------------------------------------------------------------
    def _create_mcp_server(self):
        self.mcp = FastMCP("VirtualDJ-MCP-Server",
                      instructions="Provides a bridge to communicate with VirtualDJ.",
                      on_duplicate="warn")

        self._register_tools()
        self._register_routes()
    #------------------------------------------------------------------------------------
    def get_mcp_server(self):
        return self.mcp
    #------------------------------------------------------------------------------------
    def run_mcp_server(self):
        console.print("VirtualDJ-MCP-Server starting...")
        mcp = self.mcp

        try:
            if MCP_SERVER_TRANSPORT == "stdio":
                mcp.run()
            elif MCP_SERVER_TRANSPORT == "http":
                mcp.run(transport=MCP_SERVER_TRANSPORT.lower(), host=MCP_SERVER_HOST, port=MCP_SERVER_PORT, path=MCP_SERVER_DEFAULT_PATH)
            else:
                console.print(f"MCP_SERVER_TRANSPORT error.")
        except KeyboardInterrupt:
            console.print("MCP Server shutdown requested")
        except Exception as e:
            console.print(f"MCP Server error: {e}")
            raise
        finally:
            console.print("VirtualDJ-MCP MCP Server stopped")
    #------------------------------------------------------------------------------------
    def _register_routes(self):
        mcp = self.mcp
        #--------------------------------------------------------------------------------
        @mcp.custom_route("/", methods=["GET"])
        async def api_root(request: Request) -> PlainTextResponse:
            return PlainTextResponse("VirtualDJ-MCP-Server")
        #--------------------------------------------------------------------------------
        @mcp.custom_route("/health", methods=["GET"])
        async def api_health(request: Request) -> PlainTextResponse:
            return PlainTextResponse("VirtualDJ-MCP-Server/health")
        #--------------------------------------------------------------------------------
        @mcp.custom_route("/mcp", methods=["GET"])
        async def api_mcp(request: Request) -> PlainTextResponse:
            return PlainTextResponse("VirtualDJ-MCP-Server/mcp")       
    #------------------------------------------------------------------------------------
    def _register_tools(self):
       mcp = self.mcp
       #--------------------------------------------------------------------------------
       mcp.add_tool(self.send_VirtualDJ)
       mcp.add_tool(self.set_crossfader)
    #------------------------------------------------------------------------------------
    @tool
    async def send_VirtualDJ(self, vdj_script: str) -> bool:
        """
        Send a command via a vdjscript to VirtualDJ
        """
        try:
            async with self.vdj_client:
                result = await self.vdj_client.send_async(vdj_script)
                console.print(f"vdj_client.send_async({vdj_script}) => {result}")
                return result
            result = PlainTextResponse("VirtualDJ-MCP-Server/mcp")
            return result
        except Exception as e:
            console.print(f"Error in send_VirtualDJ: {e}")
    #------------------------------------------------------------------------------------------------------------------------------------
    def _define_mcp_tools(self, mcp: FastMCP):
        #------------------------------------------------------------------------------------
        @mcp.tool()
        async def vdjscript_send(self, vdjscript: str) -> bool:
            """
            Send a command via a vdjscript to VirtualDJ
            """
            try:
                async with self.vdj_client:
                    result = await self.vdj_client.send_async(vdjscript)
                    console.print(f"vdj_client.send_async({vdjscript}) => {result}")
                    return result
            except Exception as e:
                console.print(f"Error in send_VirtualDJ: {e}")
    #------------------------------------------------------------------------------------
    @tool
    async def set_crossfader(self, position: float) -> bool:
        """
        Set the crossader in VirtualDJ at position
        """
        position = self.slider_clamp(position)
        vdj_script = f"crossfader {position}%"

        try:
            async with self.vdj_client:
                result = await self.vdj_client.send_async(vdj_script)
                console.print(f"vdj_client.send_async({vdj_script}) => {result}")
                return result
        except Exception as e:
            console.print(f"Error in set_crossfader: {e}")
    #------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _slider_clamp(x: float) -> float:
            # Clamp x to valid range [0-100]
            return max(0, min(100, x))

