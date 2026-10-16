import logging
import httpx
from mcp.server.mcpserver import MCPServer

logger = logging.getLogger(__name__)

RAG_BASE_URL = "http://localhost:8026"


def register_rag_tools(mcp: MCPServer) -> None:
    """将 RAG 相关工具注册到 MCP server。"""

    @mcp.tool()
    async def search_knowledge_base(query: str, kb_id: int = 1) -> str:
        """在 RAG 知识库中检索相关文档片段。

        当你需要查找内部知识、文档、政策、流程时使用这个工具。
        不要用它查实时新闻，实时新闻用 web_search。

        Args:
            query: 检索查询语句，用自然语言描述你想查什么
            kb_id: 知识库 ID，默认为 1
        """
        if not query.strip():
            return "错误：查询语句不能为空。"

        logger.info("RAG 检索: query=%r, kb_id=%d", query, kb_id)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 调用你的 RAG 流式问答接口
                resp = await client.post(
                    f"{RAG_BASE_URL}/api/v1/chat/stream",
                    json={"query": query, "kb_id": kb_id},
                )
                resp.raise_for_status()

                # 解析 SSE 流，提取回答和引用来源
                answer = ""
                sources = []
                for line in resp.text.split("\n"):
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            import json
                            obj = json.loads(data_str)
                            if "content" in obj:
                                answer += obj["content"]
                            if "sources" in obj:
                                sources = obj["sources"]
                        except json.JSONDecodeError:
                            pass

            # 格式化返回
            lines = [f"回答：\n{answer}\n"]
            if sources:
                lines.append("参考来源：")
                for s in sources:
                    lines.append(f"  [{s.get('index', '?')}] {s.get('file_name', '未知')}")
            return "\n".join(lines)

        except httpx.ConnectError:
            logger.error("无法连接 RAG 服务: %s", RAG_BASE_URL)
            return "错误：知识库服务暂时不可用，请稍后重试。"
        except httpx.TimeoutException:
            logger.error("RAG 服务超时")
            return "错误：知识库查询超时，请稍后重试。"
        except Exception as e:
            logger.exception("RAG 检索失败")
            return f"错误：检索失败 - {e}"