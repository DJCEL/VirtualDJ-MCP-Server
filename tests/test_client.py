import asyncio
import pytest
from fastmcp import FastMCP, Client
from mcp.types import TextContent

from src.virtualdj_mcp_server import VirtualDJMCPServer



@pytest.fixture
def mcp_server():
    mcp = FastMCP(name="TestServer")

    @mcp.tool()
    def test_connected():
        vdjclient = VirtualDJClient()
        return vdjclient.is_connected()

    return mcp

@pytest.mark.asyncio
async def test_server(mcp_server:FastMCP):
    async with Client(mcp_server) as client:
        result = await client.call_tool("test_connected")
        assert isinstance(result.content[0], TextContent)
        assert result.content[0].text == "true"

