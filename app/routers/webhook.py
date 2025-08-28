# app/routers/webhook.py
from fastapi import APIRouter, Request
from app.services import buy, sell

router = APIRouter()

@router.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    symbol = data.get("symbol")
    action = data.get("action")

    if not symbol or not action:
        return {"error": "Invalid payload"}

    action = action.upper()

    if action == "BUY":
        result = buy.execute_buy(symbol)
        return result  # ✅ 그대로 반환 (skipped_error 등 클라이언트가 그대로 확인 가능)
    
    elif action == "SELL":
        result = sell.execute_sell_all(symbol)
        return result
    
    return {"error": "Invalid action"}