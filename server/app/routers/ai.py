from urllib.request import Request

from fastapi import APIRouter
from fastapi.params import Query, Form
from langgraph.checkpoint.memory import MemorySaver
from openai import BaseModel
from starlette.responses import StreamingResponse

from typing import List, Dict, Optional
from app.agents.agent1 import  run_agent_for_web_stream
from app.agents.service_agent import run_agent_for_service_stream
from app.llm.qw_llm import llm_qwen



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


@router.get("/prompt")
async def process_prompt(
        chatId: str = Query(..., description="通过URL参数传递的chatId"),
        prompt: str = Query(..., description="通过FormData传递的prompt")
):
    async def generate():
        # 调用 service_agent 获取流式响应
        async for chunk in run_agent_for_service_stream(prompt, chatId):
            # 处理响应流 - 修正为SSE格式
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")
