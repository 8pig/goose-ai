from urllib.request import Request

from fastapi import APIRouter
from fastapi.params import Query, Form
from langgraph.checkpoint.memory import MemorySaver
from openai import BaseModel
from starlette.responses import StreamingResponse

from typing import List, Dict, Optional
from app.agents.agent1 import  run_agent_for_web_stream
from app.agents.chat import run_chat_llm_stream
from app.agents.service_agent import run_agent_for_service_stream
from app.llm.qw_llm import llm_qwen
import os


class ChatRequest(BaseModel):
    message: str

router = APIRouter(
    prefix="/ai",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)


class OpenAIChatRequest(BaseModel):
    model: str = "qwen"  # 默认模型
    messages: List[Dict[str, str]]  # OpenAI 规范的消息格式
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = True  # 是
    session_id: Optional[str] = "default_session"  # 添加这一行

@router.post("/chat/stream")
async def stream_chat(request: OpenAIChatRequest):
    user_message = request.messages[-1]["content"]
    session_id = request.session_id if hasattr(request, 'session_id') else "default_session"
    async def generate():
        async for chunk in run_agent_for_web_stream(user_message, session_id):
            yield f"data: {chunk}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")



@router.post("/chat/stream/service")
async def stream_chat(request: OpenAIChatRequest):
    user_message = request.messages[-1]["content"]
    session_id = request.session_id if hasattr(request, 'session_id') else "default_session"
    async def generate():
        async for chunk in run_agent_for_service_stream(user_message, session_id):
            yield f"data: {chunk}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/prompt")
async def process_prompt(
        chatId: str = Query(..., description="通过URL参数传递的chatId"),
        prompt: str = Form(..., description="通过FormData传递的prompt")
):
    async def generate():
        # 调用 service_agent 获取流式响应
        async for chunk in run_agent_for_service_stream(prompt, chatId):
            # 处理响应流 - 修正为SSE格式
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")



@router.post("/chat")
async def process_prompt(
        chatId: str = Query(..., description="通过URL参数传递的chatId"),
        prompt: str = Form(..., description="通过FormData传递的prompt")
):
    async def generate():
        async for chunk in run_chat_llm_stream(prompt, chatId):
            if hasattr(chunk, 'content'):
                yield chunk.content
            else:
                yield str(chunk)

    return StreamingResponse(generate(), media_type="text/plain")


@router.get("/history/chat/{chatId}")
async def get_chat_history_details(chatId: str):
    # 获取项目根目录路径
    current_file_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(current_file_dir)
    chat_file_path = os.path.join(project_root, "chat_history", "chat", f"{chatId}.json")

    # 检查文件是否存在
    if not os.path.exists(chat_file_path):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Chat history not found")

    # 读取并解析JSON文件
    import json
    from datetime import datetime

    with open(chat_file_path, 'r', encoding='utf-8') as f:
        chat_data = json.load(f)

    # 转换格式
    converted_data = []
    for item in chat_data:
        message_type = item['type']
        content = item['data']['content']

        # 转换角色
        role = 'user' if message_type == 'human' else 'assistant'

        # 创建新格式的消息对象
        converted_message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }

        converted_data.append(converted_message)

    return converted_data


@router.get("/history/chat")
async def get_chat_history():
    filenames = get_chat_filenames_without_extension('chat')
    return filenames





def get_chat_filenames_without_extension(dir: str):
    """获取根目录下chat文件夹中的文件名（去除后缀）"""
    # 获取项目根目录路径 - 需要多向上一级到达server目录
    current_file_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 得到 app 目录
    project_root = os.path.dirname(current_file_dir)  # 再向上一级得到 server 目录
    chat_dir = os.path.join(project_root, "chat_history", dir)

    # 检查目录是否存在
    if not os.path.exists(chat_dir):
        return []

    # 获取目录下所有文件
    files = os.listdir(chat_dir)
    # 去除文件扩展名，只保留文件名
    filenames_without_ext = []
    for file in files:
        if os.path.isfile(os.path.join(chat_dir, file)):  # 确保是文件而不是子目录
            filename, ext = os.path.splitext(file)
            filenames_without_ext.append(filename)

    return filenames_without_ext

