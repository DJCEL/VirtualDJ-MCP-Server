__version__ = "1.0.2"

from .mcp_server import VirtualDJMCPServer
from .mcp_server import __version__ as __virtualdjmcpserver_version__
from .virtualdj_client import VirtualDJClient
from .virtualdj_client import __version__ as __virtualdjclient_version__

__all__ = ["__version__",
           "VirtualDJMCPServer",
           "VirtualDJClient",
           "__virtualdjmcpserver_version__",
           "__virtualdjclient_version__"
           ]