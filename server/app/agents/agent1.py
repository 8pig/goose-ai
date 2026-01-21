import asyncio
import pathlib

from langchain_core.messages import AIMessage, ToolMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_community.chat_message_histories import ChatMessageHistory, FileChatMessageHistory

from langchain.agents import create_agent

from .request import get_current_weather
from ..llm.qw_llm import llm_qwen
import logging
from datetime import datetime



# def format_debug_output(step_name: str, content: str, is_tool_call = False) -> None:
#     if is_tool_call:
#         print(f'🔄 【工具调用】 {step_name}')
#         print("-" * 40)
#         print(content.strip())
#         print("-" * 40)
#     else:
#         print(f"💭 【{step_name}】")
#         print("-" * 40)
#         print(content.strip())
#         print("-" * 40)
#
#
# async def run_agent():
#     memory = MemorySaver()
#
#     prompt = PromptTemplate.from_template(template="""# 角色
# 你是一名优秀的工程师，你的名字叫做{name}""")
#
#     agent = create_agent(
#         model=llm_qwen,
#         tools=[],
#         checkpointer=memory,
#         debug=True,
#         system_prompt=SystemMessage(content=prompt.format(name="Bot")),
#     )
#
#     config = RunnableConfig(configurable={"thread_id": 1}, recursion_limit=100)
#
#     while True:
#         user_input = input("用户: ")
#
#         if user_input.lower() == "exit":
#             break
#
#         print("\n🤖 助手正在思考...")
#         print("=" * 60)
#
#         user_prompt = user_input
#
#         # 收集AI消息以便流式显示
#         full_response = ""
#
#         async for event in agent.astream_events({"messages": [user_input]}, config=config, version="v1"):
#             kind = event["event"]
#
#             if kind == "on_chat_model_stream":
#                 content = event["data"]["chunk"].content
#                 if content:
#                     # 流式输出字符
#                     for char in content:
#                         print(char, end='', flush=True)
#                         await asyncio.sleep(0.01)  # 可选：添加小延迟以模拟更自然的流式输出
#                     full_response += content
#
#         print("\n")  # 最后换行
#
#
# asyncio.run(run_agent())

def get_session_history(session_id: str):
    # if session_id not in store:
    #     store[session_id] = ChatMessageHistory()
    history_dir = pathlib.Path(__file__).parent.parent.parent / "chat_history"
    history_dir.mkdir(exist_ok=True)
    return FileChatMessageHistory(str(history_dir / f"{session_id}.json"))


async def run_agent_for_web_stream(user_input: str, session_id: str = "default_session"):
    """ 流式返回 OpenAI 规范格式 """
    chat_history = get_session_history(session_id)
    memory = MemorySaver()

    prompt = PromptTemplate.from_template(template="""
    # 角色
        你是一名优秀的助理, 能全方位的给于用户帮助, 且善于使用自身工具
    """)

    agent = create_agent(
        model=llm_qwen.bind_tools([get_current_weather]),
        tools=[get_current_weather],
        checkpointer=memory,
        debug=True,
        system_prompt=SystemMessage(content=prompt.format(name="Bot")),
    )

    # 将历史消息和当前输入组合
    messages = [msg.content for msg in chat_history.messages]
    messages.append(user_input)
    config = RunnableConfig(configurable={"thread_id": session_id}, recursion_limit=100)
    full_response = ""

    async for event in agent.astream_events({"messages": messages}, config=config, version="v1"):
        event_type = getattr(event, 'event', event.get('event')) if hasattr(event, 'get') else event.get('event')

        if event_type in ["on_chat_model_stream", "TEXT_MESSAGE_CONTENT", "TEXT_MESSAGE_CHUNK"]:
            # 处理 AI 消息
            content = extract_content_from_event(event)
            if content:
                full_response += content
                chunk_data = format_message_for_openai("assistant", content)
                import json
                yield json.dumps(chunk_data, ensure_ascii=False)

        elif event_type.startswith("TOOL"):
            # 处理工具消息
            content = extract_content_from_event(event)
            if content:
                chunk_data = format_message_for_openai("tool", content, "tool_call")
                import json
                yield json.dumps(chunk_data, ensure_ascii=False)

        elif event_type.startswith("THINKING"):
            # 处理思考过程
            content = extract_content_from_event(event)
            if content:
                chunk_data = format_message_for_openai("assistant", f"[思考: {content}]", "thinking")
                import json
                yield json.dumps(chunk_data, ensure_ascii=False)

    # 将本次对话添加到历史记录
    chat_history.add_user_message(user_input)
    chat_history.add_ai_message(full_response)


def format_message_for_openai(role: str, content: str, message_type: str = None):
    """根据消息类型生成 OpenAI 格式"""
    chunk_data = {
        "id": f"chatcmpl-{abs(hash(content))}",
        "object": "chat.completion.chunk",
        "created": int(datetime.now().timestamp()),
        "model": "qwen",
        "choices": [{
            "index": 0,
            "delta": {
                "role": role,
                "content": content
            },
            "finish_reason": None
        }]
    }
    return chunk_data


def extract_content_from_event(event) -> str:
    """从事件中提取内容"""
    # 事件可能是 StandardStreamEvent 或 CustomStreamEvent 对象
    if hasattr(event, 'data'):
        data = event.data
    elif isinstance(event, dict):
        data = event.get("data", {})
    else:
        data = {}

    content = None

    # LangChain 格式
    if hasattr(data, 'get'):
        if "chunk" in data and hasattr(data["chunk"], 'content'):
            content = data["chunk"].content
        elif "token" in data:
            content = data["token"]
        elif "output" in data:
            content = data["output"]
        elif "content" in data:
            content = data["content"]
        elif "tool_call" in data:
            content = str(data["tool_call"])
        elif "tool_result" in data:
            content = str(data["tool_result"])

    return content or ""