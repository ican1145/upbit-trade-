# app/main.py

from fastapi import FastAPI
from app.routers import webhook

app = FastAPI()

# 웹훅 라우터 등록
app.include_router(webhook.router)

@app.get("/")
def root():
    return {"message": "UPBIT AUTO BOT running"}