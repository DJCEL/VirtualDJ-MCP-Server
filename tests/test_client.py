import pytest

from virtualdj_mcp.client import VirtualDJClient


@pytest.mark.asyncio
async def test_client():
    client = VirtualDJClient()

    client_connected = client.is_running()

