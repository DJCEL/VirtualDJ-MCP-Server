#------------------------------------------------------------------------------------
# VirtualDJ MCP Server
#------------------------------------------------------------------------------------
__version__ = "1.0.13"

from fastmcp import FastMCP
from fastmcp.tools import tool
#from fastmcp.server.auth import StaticTokenVerifier
from rich.console import Console
from starlette.requests import Request
from starlette.responses import PlainTextResponse
#from starlette.applications import Starlette
#from starlette.routing import Mount
#from fastapi import FastAPI



from .mcp_server_config import MCP_SERVER_TRANSPORT, MCP_SERVER_HOST, MCP_SERVER_PORT, MCP_SERVER_DEFAULT_PATH
from .virtualdj_client import VirtualDJClient
from .mcp_server_logging import MCPServerLog

console = Console()


#------------------------------------------------------------------------------------------------------------------------------------
class VirtualDJMCPServer:
    def __init__(self):
        self.controller = self
        self.vdj_client = VirtualDJClient(self.controller)
        self.mcp_log = MCPServerLog(controller=self.controller, parent_name=__name__,useRichConsole=False)
        self.mcp = self._create_mcp_server()
    #------------------------------------------------------------------------------------
    def _create_mcp_server(self):
        """ 
        Create and configure the MCP Server. Communication uses JSON-RPC.
        It is possible to add <auth> in FastMCP() for authorization 
        For ASGI application, use app = mcp.http_app(host_origin_protection=True)
        """
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
        """
        Run the MCP Server
        If used with async, replace self.mcp.run() by self.mcp.run_async()
        It is possible to add stateless_http=True in run()
        """
        self.mcp_log.save_log(msg="VirtualDJ-MCP-Server starting...", parent_name=__name__, level="INFO")
        self.mcp_log.save_log(msg="Press CTRL+C to shutdown the MCP Server", parent_name=__name__, level="INFO")
 
        try:
            if MCP_SERVER_TRANSPORT == "stdio":
                self.mcp.run()
            elif MCP_SERVER_TRANSPORT == "http":
                self.mcp.run(transport=MCP_SERVER_TRANSPORT.lower(), host=MCP_SERVER_HOST, port=MCP_SERVER_PORT, path=MCP_SERVER_DEFAULT_PATH)
            elif MCP_SERVER_TRANSPORT == "streamable-http":
                self.mcp.run(transport=MCP_SERVER_TRANSPORT.lower(), host=MCP_SERVER_HOST, port=MCP_SERVER_PORT, path=MCP_SERVER_DEFAULT_PATH)
            else:
                self.mcp_log.save_log(msg="MCP_SERVER_TRANSPORT error.", parent_name=__name__, level="ERROR")
        except KeyboardInterrupt:
             self.mcp_log.save_log(msg="MCP Server shutdown requested", parent_name=__name__, level="INFO")
        except Exception as e:
             self.mcp_log.save_log(msg=f"MCP Server error: {e}", parent_name=__name__, level="ERROR")
        finally:
             self.mcp_log.save_log(msg="VirtualDJ-MCP MCP Server stopped", parent_name=__name__, level="INFO")
    #------------------------------------------------------------------------------------
    def _register_routes(self, mcp: FastMCP):
        """
        MCP endpoint is at /mcp
        MCP_PATH = "/mcp"
        """
        @mcp.custom_route("/health", methods=["GET"])
        async def health_check(request: Request) -> PlainTextResponse:
            return PlainTextResponse("VirtualDJ-MCP-Server/health: OK")   
    
#------------------------------------------------------------------------------------
    def _register_tools(self, mcp: FastMCP):
       mcp.add_tool(self.is_virtualdj_running)
       mcp.add_tool(self.send_vdjscript)
       mcp.add_tool(self.get_vdjscript)
       mcp.add_tool(self.play)
       mcp.add_tool(self.set_crossfader)
    #------------------------------------------------------------------------------------
    @tool
    async def is_virtualdj_running(self) -> bool:
        """
        This tool enables to know if VirtualDJ is running
         
        Returns:
            True if VirtualDJ is running, False otherwise
        """
        try:
            async with self.vdj_client:
                result = self.vdj_client.is_app_running()
                strMsgLog = f"vdj_client.is_app_running() => {result}"
                self.mcp_log.save_log(msg=strMsgLog, parent_name=__name__, level="INFO")
                return result
        except Exception as e:
                    strMsgLog = f"Error in is_virtualdj_running: {e}"
                    self.mcp_log.save_log(msg=strMsgLog, parent_name=__name__, level="ERROR")
                    return False
    #------------------------------------------------------------------------------------
    @tool
    async def send_vdjscript(self, vdjscript: str) -> bool:
        """
        This tool sends a command to VirtualDJ via a vdjscript.
        It enables VirtualDJ to do an action defined by the vdjscript.

        Args:
          vdjscript (a string): the vdjscript to use

        Returns:
           a boolean. True if the command was well executed, False otherwise
        """
        try:
            async with self.vdj_client:
                result = await self.vdj_client.send_async(vdjscript)
                strMsgLog = f"vdj_client.send_async({vdjscript}) => {result}"
                self.mcp_log.save_log(msg=strMsgLog, parent_name=__name__, level="INFO")
                return result
        except Exception as e:
            strMsgLog = f"Error in send_vdjscript: {e}"
            self.mcp_log.save_log(msg=strMsgLog, parent_name=__name__, level="ERROR")
            return False
    #------------------------------------------------------------------------------------
    @tool
    async def get_vdjscript(self, vdjscript: str) -> str:
        """
        This tool queries VirtualDJ via a vdjscript.
        It enables to get and extract data from VirtualDJ.

        Args:
          vdjscript: the vdjscript to use

        Returns:
          a string with the result of the query
        """
        try:
            async with self.vdj_client:
                result = await self.vdj_client.get_async(vdjscript)
                strMsgLog = f"vdj_client.get_async({vdjscript}) => {result}"
                self.mcp_log.save_log(msg=strMsgLog, parent_name=__name__, level="INFO")
                return result
        except Exception as e:
            strMsgLog = f"Error in get_vdjscript: {e}"
            self.mcp_log.save_log(msg=strMsgLog, parent_name=__name__, level="ERROR")
            return "error in get_vdjscript"
    #------------------------------------------------------------------------------------
    @tool
    async def play(self, deck_ref: str) -> bool:
        """
        This tool plays a song on a defined deck

        Args:
          deck_ref: the deck to use (left, right, ...)

        Returns:
            True if the song is playing, False otherwise
        """
        vdjscript = f"deck {deck_ref} play"
        try:
            async with self.vdj_client:
                result = await self.vdj_client.send_async(vdjscript)
                strMsgLog = f"vdj_client.send_async({vdjscript}) => {result}"
                self.mcp_log.save_log(msg=strMsgLog, parent_name=__name__, level="INFO")
                return result
        except Exception as e:
            strMsgLog = f"Error in play: {e}"
            self.mcp_log.save_log(msg=strMsgLog, parent_name=__name__, level="ERROR")
            return False
    #------------------------------------------------------------------------------------
    @tool
    async def set_crossfader(self, position: float) -> bool:
        """
        This tool sets the crossfader in VirtualDJ at a certain position (between 0 and 100)

        Args:
            position: the position of the crossfader (between 0 and 100)

        Returns:
            True if the crossfader position was updated, False otherwise
        """
        if not 0.0 <= position <= 100.0:
            strMsgLog = "Crossfader position must be between 0 and 100"
            self.mcp_log.save_log(msg=strMsgLog, parent_name=__name__, level="ERROR")
            return False

        vdjscript = f"crossfader {position}%"

        try:
            async with self.vdj_client:
                result = await self.vdj_client.send_async(vdjscript)
                strMsgLog = f"vdj_client.send_async({vdjscript}) => {result}"
                self.mcp_log.save_log(msg=strMsgLog, parent_name=__name__, level="INFO")
                return result
        except Exception as e:
            strMsgLog = f"Error in set_crossfader: {e}"
            self.mcp_log.save_log(msg=strMsgLog, parent_name=__name__, level="ERROR")
            return False