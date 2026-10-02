# VirtualDJ-MCP-Server
MCP server for VirtualDJ software

![alt text](https://github.com/djcel/VirtualDJ-MCP-Server/blob/main/schema.png?raw=true "")

Use "mcp.json" after updating the directory.
The mcp.json file uses "uv" (fast Python package and project manager that replaces multiple tools like pip, pip-tools, pipx, poetry, pyenv, and virtualenv with a single binary) to run/launch the MCP server.
If you want to change the type ("stdio" for local/Claude or "http" for remote), you also need to update "MCP_SERVER_TRANSPORT" in the mcp_server_config.py file


You can test/debug the MCP server with MCP Inspector.