import sys
from fastmcp import FastMCP

from rich.console import Console
console = Console(file=sys.stderr)

from starlette.requests import Request
from starlette.responses import PlainTextResponse
from pydantic import BaseModel, Field

from config import MCP_SERVER_TRANSPORT, MCP_SERVER_HOST, MCP_SERVER_PORT, MCP_SERVER_DEFAULT_PATH
from virtualdj_client import VDJError, VirtualDJClient

#------------------------------------------------------------------------------------------------------------------------------------
class DeckStatus(BaseModel):
    """Current status of a DJ deck"""
    deck_id: int = Field(description="Deck number (1-8)")
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

#------------------------------------------------------------------------------------------------------------------------------------
def define_mcp_server_api_routes(mcp: FastMCP,vdj_client):

    @mcp.custom_route("/", methods=["GET"])
    async def api_root(request: Request) -> PlainTextResponse:
        result = PlainTextResponse("VirtualDJ-MCP-Server")
        return result

    """
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
    """
#------------------------------------------------------------------------------------------------------------------------------------
def define_mcp_server_api_tools(mcp: FastMCP, vdj_client):

    # ==================== DECK CONTROL SUITE ====================
    @mcp.tool()
    async def get_deck_status(deck_id: int) -> DeckStatus:
        """
        Get current status of a specific deck

        Args:
            deck_id: Deck number (1-8)

        Returns:
            Current deck status and track information
        """
        try:
            async with vdj_client:
                # Get deck variables (VirtualDJ variable names)
                commands = [
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
                for cmd in commands:
                    result = await vdj_client.send_command(cmd)
                    if result["status"] == "success":
                        var_name = cmd.split("'")[1]
                        results[var_name] = result["result"]

                # Parse results into DeckStatus
                return DeckStatus(
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

        except Exception as e:
            console.print(f"[red]Error in get_deck_status: {e}[/red]")
            # Return a default deck status on error
            return DeckStatus(
                deck_id=deck_id,
                is_playing=False,
                track_title="Error",
                track_artist="Unknown",
                position=0.0,
                duration=0.0,
                volume=0,
                pitch=0.0,
            )

    @mcp.tool()
    async def play_pause_deck(deck_id: int, action: str = "toggle") -> DeckStatus:
        """
        Control playback on a specific deck

        Args:
            deck_id: Deck number (1-8)
            action: Action to perform (play, pause, toggle)

        Returns:
            Updated deck status
        """
        try:
            if action == "play":
                cmd = f"deck {deck_id} play"
            elif action == "pause":
                cmd = f"deck {deck_id} pause"
            else:  # toggle
                cmd = f"deck {deck_id} play_pause"

            async with vdj_client:
                result = await vdj_client.send_command(cmd)

                if result["status"] != "success":
                    raise VDJError(f"Failed to {action} deck {deck_id}: {result.get('error', 'Unknown error')}")

                console.print(f"[green]Deck {deck_id}: {action}[/green]")
                # Get updated deck status
                return await get_deck_status(deck_id)

        except Exception as e:
            console.print(f"[red]Error in play_pause_deck: {e}[/red]")
            raise VDJError(str(e))


    @mcp.tool()
    async def load_track_to_deck(deck_id: int, track_path: str) -> DeckStatus:
        """
        Load a track to a specific deck

        Args:
            deck_id: Deck number (1-8)
            track_path: Path to audio file or library reference

        Returns:
            Updated deck status with loaded track
        """
        try:
            # Validate track path
            if not Path(track_path).exists():
                raise VDJError(f"Track file not found: {track_path}")

            cmd = f"deck {deck_id} load '{track_path}'"

            async with client:
                result = await vdj_client.send_command(cmd)

                if result["status"] != "success":
                    raise VDJError(f"Failed to load track to deck {deck_id}: {result.get('error', 'Unknown error')}")

                console.print(f"[green]Loaded '{Path(track_path).name}' to deck {deck_id}[/green]")
                return await get_deck_status(deck_id)

        except Exception as e:
            console.print(f"[red]Error in load_track_to_deck: {e}[/red]")
            raise VDJError(str(e))

#------------------------------------------------------------------------------------------------------------------------------------
def define_mcp_server_api_resources(mcp: FastMCP,vdj_client):
    return
#------------------------------------------------------------------------------------------------------------------------------------
def define_mcp_server_api_prompts(mcp: FastMCP,vdj_client):
    return
#------------------------------------------------------------------------------------------------------------------------------------
def define_mcp_server_api(mcp: FastMCP, vdj_client):
    define_mcp_server_api_tools(mcp,vdj_client)
    define_mcp_server_api_resources(mcp,vdj_client)
    define_mcp_server_api_prompts(mcp,vdj_client)
    define_mcp_server_api_routes(mcp,vdj_client) 
#------------------------------------------------------------------------------------------------------------------------------------
def create_mcp_server(vdj_client):
    mcp = FastMCP("VirtualDJ-MCP",
                  instructions="Provides an API to communicate with VirtualDJ.",
                  on_duplicate="warn")

    define_mcp_server_api(mcp,vdj_client)

    if MCP_SERVER_TRANSPORT == "stdio":
        mcp.run()
    elif MCP_SERVER_TRANSPORT == "http":
        mcp.run(transport=MCP_SERVER_TRANSPORT.lower(), host=MCP_SERVER_HOST, port=MCP_SERVER_PORT, path=MCP_SERVER_DEFAULT_PATH)
    else:
        console.print(f"[red]MCP_SERVER_TRANSPORT error.[/red]")
#------------------------------------------------------------------------------------------------------------------------------------
def run_mcp_server(vdj_client):
    console.print("[green]VirtualDJ-MCP-Server starting...[/green]")

    try:
        create_mcp_server(vdj_client)
    except KeyboardInterrupt:
        console.print("[yellow]MCP Server shutdown requested[/yellow]")
    except Exception as e:
        console.print(f"[red]MCP Server error: {e}[/red]")
        raise
    finally:
        console.print("[green]VirtualDJ-MCP MCP Server stopped[/green]")
