from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

llm_qwen = ChatOpenAI(
    model="qwen-max-latest",
    # model="qwen3-235b-a22b",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
    # api_key=key,
    verbose=True,
    streaming=True,
)
