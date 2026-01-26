import os
import uuid

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory
from app.llm.qw_llm import llm_qwen
from langchain_community.chat_message_histories import FileChatMessageHistory
from app.prompt.game_prompt import game_prompt

def get_session_history(session_id: str):
    """获取会话历史存储对象"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chat_history_dir = os.path.join(project_root, "chat_history")
    os.makedirs(chat_history_dir, exist_ok=True)
    return FileChatMessageHistory(os.path.join(chat_history_dir, f"{session_id}.json"))


# 创建带会话历史的链
chain = game_prompt | llm_qwen | StrOutputParser()

agent_with_game_history = RunnableWithMessageHistory(
    runnable=chain,
    get_session_history=get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history"
)



