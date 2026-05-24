from fastmcp import FastMCP

from helix.utils import logger

mcp = FastMCP("Helix 🧠")


if __name__ == "__main__":
    logger.info("Starting Helix MCP server")
    mcp.run()
