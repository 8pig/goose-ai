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

from app.utils.get_json_file import get_chat_filenames_without_extension
from app.agents.game_chat import agent_with_game_history  # 导入 agent

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
    session_id: Optional[str] = "default_session"


@router.get("/game")
async def process_prompt(
        chatId: str = Query(..., description="通过URL参数传递的chatId"),
        prompt: str = Query(..., description="通过Query传递的prompt")
):
    async def generate():
        full_response = ""
        async for chunk in agent_with_game_history.astream(
            {
                "question": prompt,
                "+-原谅值增减": "0",
                "女友心情": "正常",
                "女友说的话": "",
                "当前原谅值": "100"
            },
            config={"configurable": {"session_id": chatId}}
        ):
            full_response += chunk
            yield chunk  # 直接返回原始块内容，不加 data: 前缀

    return StreamingResponse(generate(), media_type="text/plain")