import os

from fastapi import FastAPI
from app.routers import users, ai
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

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
