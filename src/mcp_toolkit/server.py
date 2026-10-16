from mcp.server.mcpserver import MCPServer

mcp = MCPServer("RAG Toolkit")


@mcp.tool()
def add(a: int, b: int) -> int:
    """把两个数字相加。用来验证 MCP 链路是否通畅。

    Args:
        a: 第一个数字
        b: 第二个数字
    """
    return a + b


if __name__ == "__main__":
    mcp.run()