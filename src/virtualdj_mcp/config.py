# VirtualDJ - MCP Server
MCP_SERVER_TRANSPORT = "http"  # "stdio" or "http"
MCP_SERVER_HOST = "127.0.0.1" # default: "127.0.0.1"
MCP_SERVER_PORT = 9000 # default: 9000
MCP_SERVER_DEFAULT_PATH = "/mcp"  # default: "/" (HTTP only)

# VirtualDJ - Network Control Plugin (HTTP Server)
VDJ_NETWORK_CONTROL_HOST = "127.0.0.1" # default: "127.0.0.1"
VDJ_NETWORK_CONTROL_PORT = 80 # default: 80
VDJ_NETWORK_CONTROL_PASSWORD = None # default None
VDJ_NETWORK_CONTROL_TIMEOUT = 10.0  # default: 10 seconds
VDJ_NETWORK_CONTROL_DEBUG = True # default (bool): True

# VirtualDJ - Process name in tasks manager
VDJ_PROCESS_NAME = "virtualdj"
VDJ_PROCESS_PATH_WINDOWS = r"C:\Program Files\VirtualDJ\virtualdj.exe"
VDJ_PROCESS_PATH_MAC = "/Applications/VirtualDJ.app"