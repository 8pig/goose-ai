import os

from fastapi import FastAPI
from app.routers import users, chat, game, service, chat_pdf
from dotenv import load_dotenv
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


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
app.include_router(game.router)
app.include_router(service.router)
app.include_router(chat_pdf.router)

app.mount("/static", StaticFiles(directory="static", check_dir=True), name="static")



@app.get("/")
async def root():
    print("Hello from fastapi-ai!")
    return {"message": "Hello World"}

async def  main():
    print("Hello from fastapi-ai")


# 在 main.py 中
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="localhost", port=port, reload=True)

