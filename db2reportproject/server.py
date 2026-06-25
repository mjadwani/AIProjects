from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Monitoring Server")

@mcp.tool()
def get_cpu_usage() -> str:
    return "Current CPU Usage = 72%"

@mcp.tool()
def get_db2_status() -> str:
    return "DB2 subsystem PROD1 is healthy"

@mcp.resource("system://version")
def get_version():
    return "Monitoring Server v1.0"




if __name__ == "__main__":
    mcp.run()