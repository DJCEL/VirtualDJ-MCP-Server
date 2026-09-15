#------------------------------------------------------------------------------------
# VirtualDJ MCP Server
#------------------------------------------------------------------------------------
__version__ = "1.0.12"

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
        self.mcp = self._create_mcp_server()
    #------------------------------------------------------------------------------------
    def _create_mcp_server(self):
        mcp = FastMCP("VirtualDJ-MCP-Server",
                      instructions="Provides a bridge to communicate with VirtualDJ.",
                      on_duplicate="warn")

        self._register_tools(mcp)
        self._register_routes(mcp)

        return mcp
    #------------------------------------------------------------------------------------
    def get_mcp_server(self):
        return self.mcp
    #------------------------------------------------------------------------------------
    def run_mcp_server(self):
        console.print("VirtualDJ-MCP-Server starting...")
 
        try:
            if MCP_SERVER_TRANSPORT == "stdio":
                self.mcp.run()
            elif MCP_SERVER_TRANSPORT == "http":
                self.mcp.run(transport=MCP_SERVER_TRANSPORT.lower(), host=MCP_SERVER_HOST, port=MCP_SERVER_PORT, path=MCP_SERVER_DEFAULT_PATH)
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
    def _register_routes(self, mcp: FastMCP):
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
    def _register_tools(self, mcp: FastMCP):
       mcp.add_tool(self.send_vdjscript)
       mcp.add_tool(self.get_vdjscript)
       mcp.add_tool(self.play)
       mcp.add_tool(self.set_crossfader)
    #------------------------------------------------------------------------------------
    @tool
    async def send_vdjscript(self, vdjscript: str) -> bool:
        """
        This tool sends a command to VirtualDJ via a vdjscript.
        It enables VirtualDJ to do an action defined by the vdjscript.
        """
        try:
            async with self.vdj_client:
                result = await self.vdj_client.send_async(vdjscript)
                console.print(f"vdj_client.send_async({vdjscript}) => {result}")
                return result
        except Exception as e:
            console.print(f"Error in send_vdjscript: {e}")
            raise
    #------------------------------------------------------------------------------------
    @tool
    async def get_vdjscript(self, vdjscript: str) -> str:
        """
        This tool queries VirtualDJ via a vdjscript.
        It enables to get and extract data from VirtualDJ.
        """
        try:
            async with self.vdj_client:
                result = await self.vdj_client.get_async(vdjscript)
                console.print(f"vdj_client.get_async({vdjscript}) => {result}")
                return result
        except Exception as e:
            console.print(f"Error in get_vdjscript: {e}")
            raise
    #------------------------------------------------------------------------------------
    @tool
    async def play(self, deck_ref:str) -> bool:
        """
        This tool plays a song on a defined deck
        """
        vdjscript = f"deck {deck_ref} play"
        try:
            async with self.vdj_client:
                result = await self.vdj_client.send_async(vdjscript)
                console.print(f"vdj_client.send_async({vdjscript}) => {result}")
                return result
        except Exception as e:
            console.print(f"Error in play: {e}")
            raise
    #------------------------------------------------------------------------------------
    @tool
    async def set_crossfader(self, position: float) -> bool:
        """
        This tool sets the crossfader in VirtualDJ at a certain position (between 0 and 100)
        """
        if not 0.0 <= position <= 100.0:
            raise ValueError("Crossfader position must be between 0 and 100")
        vdjscript = f"crossfader {position}%"

        try:
            async with self.vdj_client:
                result = await self.vdj_client.send_async(vdjscript)
                console.print(f"vdj_client.send_async({vdjscript}) => {result}")
                return result
        except Exception as e:
            console.print(f"Error in set_crossfader: {e}")
            raise