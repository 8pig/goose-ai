import os
import uuid

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory
from app.llm.qw_llm import llm_qwen
from app.prompt.service_prompt import service_prompt
from langchain_community.chat_message_histories import FileChatMessageHistory


def get_session_history(session_id: str):
    """获取会话历史存储对象"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chat_history_dir = os.path.join(project_root, "chat_history")
    os.makedirs(chat_history_dir, exist_ok=True)
    return FileChatMessageHistory(os.path.join(chat_history_dir, f"{session_id}.json"))


# 创建带会话历史的链
chain = service_prompt | llm_qwen | StrOutputParser()

agent_with_chat_history = RunnableWithMessageHistory(
    runnable=chain,
    get_session_history=get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history"
)


async def run_agent_for_service_stream(question: str, session_id: str = None):
    """运行服务代理并返回流式响应

    Args:
        question: 用户问题
        session_id: 会话ID，如果不提供则自动生成
    """
    if session_id is None:
        session_id = str(uuid.uuid4())

    async for chunk in agent_with_chat_history.astream(
            {
                "court_name": "河北省文安县法院",
                "service_name": "司法智能客服",
                "chat_history": [],
                "question": question
            },
            config={"configurable": {"session_id": session_id}}
    ):
        print(chunk, end="")
        yield chunk
