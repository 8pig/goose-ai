from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
import uuid

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory
from app.llm.qw_llm import llm_qwen
from app.prompt.service_prompt import service_prompt
from langchain_community.chat_message_histories import FileChatMessageHistory


multi_chat_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    1. 你是一位幽默且有爱的对话机器人, 你叫{name}， 擅长帮助用户处理问题各种问题
    """),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])



def get_session_history(session_id: str):
    """获取会话历史存储对象"""
    # 获取 server 目录路径
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    server_dir = os.path.dirname(os.path.dirname(current_file_dir))
    chat_history_dir = os.path.join(server_dir, "chat_history")
    os.makedirs(chat_history_dir, exist_ok=True)
    # 在 chat_history_dir 下添加子文件夹
    chat_subdir = os.path.join(chat_history_dir, "chat")
    os.makedirs(chat_subdir, exist_ok=True)
    return FileChatMessageHistory(os.path.join(chat_subdir, f"{session_id}.json"))





# 创建带会话历史的链
chain = multi_chat_prompt | llm_qwen | StrOutputParser()

agent_with_chat_history = RunnableWithMessageHistory(
    runnable=chain,
    get_session_history=get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history"
)


async def run_chat_llm_stream(question: str, session_id: str = None):
    """运行服务代理并返回流式响应

    Args:
        question: 用户问题
        session_id: 会话ID，如果不提供则自动生成
    """
    if session_id is None:
        session_id = str(uuid.uuid4())

    async for chunk in agent_with_chat_history.astream(
            {
                "name": "野猪佩奇",
                "question": question
            },
            config={"configurable": {"session_id": session_id}}
    ):
        print(chunk, end="")
        yield chunk
