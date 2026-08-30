import sys
import asyncio
from fastmcp import FastMCP
#from mcp.server.fastmcp import FastMCP
from rich.console import Console
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from pydantic import BaseModel, Field
#from urllib.parse import quote, urlparse

from config import MCP_SERVER_TRANSPORT, MCP_SERVER_HOST, MCP_SERVER_PORT, MCP_SERVER_DEFAULT_PATH
from client import VirtualDJClient, VDJError

console = Console(file=sys.stderr)

#------------------------------------------------------------------------------------------------------------------------------------
class DeckStatus(BaseModel):
    """Current status of a DJ deck"""
    deck_id: int = Field(description="Deck number")
    is_playing: bool = Field(description="Whether deck is currently playing")
    track_path: str | None = Field(description="Path to currently loaded track")
    track_title: str | None = Field(description="Track title")
    track_artist: str | None = Field(description="Track artist")
    position: float = Field(description="Current position in seconds")
    duration: float = Field(description="Track duration in seconds")
    bpm: float | None = Field(description="Beats per minute")
    key: str | None = Field(description="Musical key")
    volume: int = Field(description="Deck volume (0-100)")
    pitch: float = Field(description="Pitch adjustment (-100 to +100)")
    gain: float = Field(description="Gain adjustment (-100 to +100)")
    eq_high: float = Field(description="Eq High adjustment (-100 to +100)")
    eq_mid: float = Field(description="Eq Mid adjustment (-100 to +100)")
    eq_low: float = Field(description="Eq Low adjustment (-100 to +100)")
    color_fx: float = Field(description="ColorFX adjustment (-100 to +100)")
#------------------------------------------------------------------------------------------------------------------------------------
class MixerStatus(BaseModel):
    """Status of the DJ mixer"""
    crossfader_position: float = Field(description="Crossfader position (-100 to +100)")
    master_volume: int = Field(description="Master volume (0-100)")
    headphone_volume: int = Field(description="Headphone volume (0-100)")
    headphone_cue: str = Field(description="Headphone cue selection (deck1, deck2, master)")
    headphone_mix:int = Field(description="Headphone mix (0-100)")
#------------------------------------------------------------------------------------------------------------------------------------
def define_mcp_routes(mcp: FastMCP,vdj_client: VirtualDJClient):

    @mcp.custom_route("/", methods=["GET"])
    async def api_root(request: Request) -> PlainTextResponse:
        result = PlainTextResponse("VirtualDJ-MCP-Server")
        return result

    @mcp.custom_route("/mcp", methods=["GET"])
    async def api_root(request: Request) -> PlainTextResponse:
        result = PlainTextResponse("VirtualDJ-MCP-Server")
        return result

#------------------------------------------------------------------------------------------------------------------------------------
def define_mcp_tools(mcp: FastMCP, vdj_client: VirtualDJClient):

    #""" We can use prefab_ui to give our tool a UI """
    #@mcp.tool(app=True)

    @mcp.tool()
    async def get_deck_status(deck_id: int) -> DeckStatus:
        try:
            async with vdj_client:
                # Get deck variables (VirtualDJ variable names)
                vdj_script_list = [
                    f"get_var 'deck{deck_id}_play'",
                    f"get_var 'deck{deck_id}_title'",
                    f"get_var 'deck{deck_id}_artist'",
                    f"get_var 'deck{deck_id}_position'",
                    f"get_var 'deck{deck_id}_duration'",
                    f"get_var 'deck{deck_id}_bpm'",
                    f"get_var 'deck{deck_id}_key'",
                    f"get_var 'deck{deck_id}_volume'",
                    f"get_var 'deck{deck_id}_pitch'",
                ]

                results = {}
                for vdj_script in vdj_script_list:
                    result = await vdj_client.get_async(vdj_script)
                    var_name = vdj_script.split("'")[1]
                    results[var_name] = result["result"]

                result_final = DeckStatus(
                    deck_id=deck_id,
                    is_playing=results.get(f"deck{deck_id}_play", "0") == "1",
                    track_title=results.get(f"deck{deck_id}_title", "No Track"),
                    track_artist=results.get(f"deck{deck_id}_artist", "Unknown Artist"),
                    position=float(results.get(f"deck{deck_id}_position", 0)),
                    duration=float(results.get(f"deck{deck_id}_duration", 0)),
                    bpm=float(results.get(f"deck{deck_id}_bpm", 0)) if results.get(f"deck{deck_id}_bpm") else None,
                    key=results.get(f"deck{deck_id}_key"),
                    volume=int(results.get(f"deck{deck_id}_volume", 100)),
                    pitch=float(results.get(f"deck{deck_id}_pitch", 0)),
                )

                return result_final

        except Exception as e:
            console.print(f"Error in get_deck_status: {e}")
            result_final = DeckStatus(
                deck_id=deck_id,
                is_playing=False,
                track_title="Error",
                track_artist="Unknown",
                position=0.0,
                duration=0.0,
                volume=0,
                pitch=0.0,
            )
            return result_final
    #------------------------------------------------------------------------------------
    @mcp.tool()
    async def play_pause_deck(deck_id: int, action: str = "toggle") -> bool:
        try:
            if action == "play":
                vdj_script = f"deck {deck_id} play"
            elif action == "pause":
                vdj_script = f"deck {deck_id} pause"
            else:  # toggle
                vdj_script = f"deck {deck_id} play_pause"

            async with vdj_client:
                result = await vdj_client.send_async(vdj_script)
                console.print(f"Deck {deck_id}: {action}")
                return result

        except Exception as e:
            console.print(f"Error in play_pause_deck: {e}")
            raise VDJError(str(e))

    #------------------------------------------------------------------------------------
    @mcp.tool()
    async def set_crossfader_position(position: float) -> bool:
        try:
            # Clamp position to valid range
            position = max(-100, min(100, position))

            # Convert to VirtualDJ format (0-100 where 50 is center)
            vdj_position = (position + 100) / 2

            vdj_script = f"crossfader {vdj_position}%"

            async with vdj_client:
                result = await vdj_client.send_async(vdj_script)
                console.print(f"Crossfader set to {position}")
                return result

        except Exception as e:
            console.print(f"Error in set_crossfader_position: {e}")
            raise VDJError(str(e))
#------------------------------------------------------------------------------------------------------------------------------------
def create_mcp_server(vdj_client: VirtualDJClient):
    mcp = FastMCP("VirtualDJ-MCP",
                  instructions="Provides an API to communicate with VirtualDJ.",
                  on_duplicate="warn")

    define_mcp_tools(mcp,vdj_client)
    define_mcp_routes(mcp,vdj_client)
    #define_mcp_ressources(mcp,vdj_client) 

    return mcp
#------------------------------------------------------------------------------------------------------------------------------------
def run_mcp_server(vdj_client: VirtualDJClient):
    console.print("VirtualDJ-MCP-Server starting...")
    try:
        mcp = create_mcp_server(vdj_client)
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
#------------------------------------------------------------------------------------------------------------------------------------
def main():
   # Initialize VirtualDJ client
    client = VirtualDJClient()

    # Check if VirtualDJ is running
    client_running = client.is_app_running()
    console.print(f"VirtualDJ running => {client_running}")

    # Launch VirtualDJ if not running
    if client_running == False:
        console.print("Launching VirtualDJ...")
        client_launching = client.open_app()
        console.print(f"VirtualDJ launching => {client_launching}")
        client_running = client.is_app_running()
        console.print(f"VirtualDJ running => {client_running}")
        if (client_running == False):
            sys.exit()

    # Check the NetWork Control plugin
    client_connected = client.is_connected()
    console.print(f"VirtualDJ NetWork Control plugin connected => {client_connected}")
    if (client_connected == False):
        console.print("Check that the NetWork Control plugin is available and activated in VirtualDJ")
        sys.exit()

    run_mcp_server(client)

#------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()