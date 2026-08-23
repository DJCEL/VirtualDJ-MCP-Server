""" VirtualDJ HTTP API client using Network Control Plugin """
import httpx
from pathlib import Path
from typing import Any
import psutil
#from urllib.parse import quote

from config import VDJ_NETWORK_CONTROL_HOST, VDJ_NETWORK_CONTROL_PORT, VDJ_NETWORK_CONTROL_PASSWORD, VDJ_NETWORK_CONTROL_TIMEOUT
from config import VDJ_PROCESS_NAME 

#------------------------------------------------------------------------------------------------------------------------------------
class VDJError(Exception):
    """VirtualDJ operation error"""
    pass
#------------------------------------------------------------------------------------------------------------------------------------
class VirtualDJClient:
    def __init__(self):
        self.base_url = f"http://{VDJ_NETWORK_CONTROL_HOST}:{VDJ_NETWORK_CONTROL_PORT}"
        self._client: httpx.AsyncClient | None = None
    #------------------------------------------------------------------------------------
    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=VDJ_NETWORK_CONTROL_TIMEOUT)
        return self
    #------------------------------------------------------------------------------------
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
            self._client = None
    #------------------------------------------------------------------------------------
    def _get_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "text/plain"}
        if VDJ_NETWORK_CONTROL_PASSWORD:
            headers["Authorization"] = f"Bearer {VDJ_NETWORK_CONTROL_PASSWORD}"
        return headers
    #------------------------------------------------------------------------------------
    async def is_running(self) -> bool:
        """ Check if VirtualDJ is running and Network Control Plugin is responding """
       
        # First check process
        for proc in psutil.process_iter(["pid", "name"]):
            process_name = proc.info["name"].lower()
            if process_name and VDJ_PROCESS_NAME in process_name:
                # Process running, check HTTP API
                try:
                    script = "nop"
                    response = await self.execute(script)
                    return (response.status_code == 200)
                except Exception:
                    return False  # Process running but plugin not responding
        
        return False
    #------------------------------------------------------------------------------------       
    async def send_command(self, command: str) -> dict[str, Any]:
        """Send VDJScript command via HTTP API"""
        return await self._send_http_command(command, is_query=False)
    #------------------------------------------------------------------------------------
    async def execute(self, script: str) -> bool:
        """Execute VDJScript and return success status"""
        result = await self.send_command(script)
        return result.get("status") == "success" and result.get("result", "").lower() == "true"
    #------------------------------------------------------------------------------------
    async def query(self, script: str) -> dict[str, Any]:
        """Query VirtualDJ for information via HTTP API"""
        return await self._send_http_command(script, is_query=True)
    #------------------------------------------------------------------------------------
    async def _send_http_command(self, script: str, is_query: bool = False) -> dict[str, Any]:
        """Send command via HTTP Network Control Plugin API"""
        endpoint = "query" if is_query else "execute"
        headers = self._get_headers()
        vdj_script_url = f"{self.base_url}/{endpoint}"
        vdj_script_url_full = f"{vdj_script_url}?script={script}"

        try:
            async with httpx.AsyncClient(timeout=VDJ_NETWORK_CONTROL_TIMEOUT) as client:
                #response = await client.post(vdj_script_url, params={"script": script}, headers=headers)
                response = await client.get(vdj_script_url_full, headers=headers)
                if response.status_code == 200:
                    result = response.text.strip()
                    if is_query:
                        return {"status": "success", "result": result}
                    else:
                        success = result.lower() == "true"
                        return {"status": "success" if success else "error", "result": result}
                elif response.status_code == 401:
                    return {"status": "error", "error": "Authentication failed - check password"}
                else:
                    return {"status": "error", "error": f"HTTP {response.status_code}: {response.text}"}

        except httpx.ConnectError:
            return {"status": "error", "error": "Cannot connect to VirtualDJ Network Control Plugin. Is it enabled?"}
        except httpx.TimeoutException:
            return {"status": "error", "error": "Command timeout"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    #------------------------------------------------------------------------------------
    #  Examples for VirtualDJ query
    #------------------------------------------------------------------------------------
    async def get_variable(self, variable: str) -> Any:
        """Get a VirtualDJ variable value"""
        result = await self.query(f"get_var '{variable}'")
        if result["status"] == "success":
            return result.get("result", "")
        else:
            raise VDJError(f"Failed to get variable {variable}: {result.get('error', 'Unknown error')}")
    #------------------------------------------------------------------------------------
    async def get_deck_info(self, deck_id: int) -> dict[str, Any]:
        """Get comprehensive deck information"""
        info = {}
        queries = {
            "title": f"deck {deck_id} get_title",
            "artist": f"deck {deck_id} get_artist",
            "bpm": f"deck {deck_id} get_bpm",
            "key": f"deck {deck_id} get_key",
            "position": f"deck {deck_id} get_position",
            "duration": f"deck {deck_id} get_songlength",
            "is_playing": f"deck {deck_id} get_isplaying",
        }

        for key, script in queries.items():
            result = await self.query(script)
            if result["status"] == "success":
                info[key] = result["result"]
            else:
                info[key] = None

        return info
    #------------------------------------------------------------------------------------
    # Examples for VirtualDJ execute
    #------------------------------------------------------------------------------------
    async def play(self, deck_id: int) -> bool:
        """Start playback on a deck"""
        cmd = f"deck {deck_id} play"
        return await self.execute(cmd)
    #------------------------------------------------------------------------------------
    async def pause(self, deck_id: int) -> bool:
        """Pause playback on a deck"""
        cmd = f"deck {deck_id} pause"
        return await self.execute(cmd)
    #------------------------------------------------------------------------------------
    async def stop(self, deck_id: int) -> bool:
        """Stop playback on a deck"""
        cmd = f"deck {deck_id} stop"
        return await self.execute(cmd)
    #------------------------------------------------------------------------------------