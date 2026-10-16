import logging
from mcp.server.mcpserver import MCPServer

logger = logging.getLogger(__name__)


def register_rag_tools(mcp: MCPServer) -> None:
    """将 RAG 相关工具注册到 MCP server。"""

    @mcp.tool()
    async def search_knowledge_base(query: str, top_k: int = 5) -> str:
        """在 RAG 知识库中检索相关文档片段。

        Args:
            query: 检索查询语句，用自然语言描述你想查什么
            top_k: 返回结果数量，默认 5，范围 1-20
        """
        if not query.strip():
            return "错误：查询语句不能为空。"
        if not 1 <= top_k <= 20:
            return "错误：top_k 必须在 1 到 20 之间。"

        logger.info("RAG 检索: query=%r, top_k=%d", query, top_k)

        documents = [
            {
                "content": f"这是关于「{query}」的模拟文档片段 1。"
                           f"实际接入 RAG 后这里会返回真实内容。",
                "source": "mock_doc_1.md",
                "score": 0.92,
            },
            {
                "content": f"这是关于「{query}」的模拟文档片段 2。"
                           f"用于验证 MCP 工具的参数传递和返回格式。",
                "source": "mock_doc_2.md",
                "score": 0.85,
            },
        ][:top_k]

        if not documents:
            return f"未找到与「{query}」相关的文档。"

        lines = [f"找到 {len(documents)} 条相关文档：\n"]
        for i, doc in enumerate(documents, 1):
            lines.append(f"[{i}] {doc['content']}")
            lines.append(f"    来源: {doc['source']} | 相关度: {doc['score']:.2f}")
            lines.append("")
        return "\n".join(lines)