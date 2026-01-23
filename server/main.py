import os

from fastapi import FastAPI
from app.routers import users, chat
from dotenv import load_dotenv
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()
app = FastAPI()
origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # 生产环境建议指定域名
    allow_credentials=True,
    allow_methods=["*"], # 允许所有方法
    allow_headers=["*"], # 允许所有请求头
)
app.include_router(users.router)
app.include_router(chat.router)



@app.get("/")
async def root():
    print("Hello from fastapi-ai!")
    return {"message": "Hello World"}

async def  main():
    print("Hello from fastapi-ai")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # 默认端口8000，可从环境变量覆盖
    uvicorn.run(app, host="0.0.0.0", port=port)
