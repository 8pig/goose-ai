import os

from fastapi import FastAPI
from app.routers import users, ai
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应具体指定
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)
app.include_router(users.router)
app.include_router(ai.router)



@app.get("/")
async def root():
    print("Hello from fastapi-ai!")
    return {"message": "Hello World"}

async def  main():
    print("Hello from fastapi-ai")


if __name__ == "__main__":
    main()
