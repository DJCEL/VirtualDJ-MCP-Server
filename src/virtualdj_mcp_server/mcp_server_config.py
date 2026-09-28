# MCP Server - Debug
MCP_SERVER_DEBUG = True # default (bool): True
MCP_SERVER_LOG_FOLDER = './log'
MCP_SERVER_LOG_FILENAME = 'mcp_server.log'


# VirtualDJ - MCP Server
MCP_SERVER_TRANSPORT = "stdio"  # "stdio" for local or "http" for remote
MCP_SERVER_HOST = "127.0.0.1" # default: "127.0.0.1"
MCP_SERVER_PORT = 9000 # default: 9000
MCP_SERVER_DEFAULT_PATH = "/mcp"  # default: "/mcp" (HTTP only)