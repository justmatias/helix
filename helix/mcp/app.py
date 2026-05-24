from fastmcp import FastMCP

from helix.utils import logger

from .tools import TOOLS

mcp = FastMCP("Helix 🧠")


def run_mcp_server() -> None:
    logger.info("Starting Helix MCP server")
    for tool in TOOLS:
        mcp.add_tool(tool)
    mcp.run()
