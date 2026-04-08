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
    profile = "webhook1"  # 복리

    if action == "BUY":
        result = buy.execute_buy(symbol, profile=profile)
        return {"message": f"Buy executed for {symbol}", "result": result}

    elif action == "SELL":
        result = sell.execute_sell_all(symbol, profile=profile)
        return {"message": f"Sell executed for {symbol}", "result": result}

    return {"error": "Invalid action"}


@router.post("/webhook2")
async def webhook2(request: Request):
    data = await request.json()
    symbol = data.get("symbol")
    action = data.get("action")

    if not symbol or not action:
        return {"error": "Invalid payload"}

    action = action.upper()
    profile = "webhook2"  # 고정자본(INITIAL_CAPITAL)

    if action == "BUY":
        result = buy.execute_buy(symbol, profile=profile)
        return {"message": f"[webhook2] Buy executed for {symbol}", "result": result}

    elif action == "SELL":
        result = sell.execute_sell_all(symbol, profile=profile)
        return {"message": f"[webhook2] Sell executed for {symbol}", "result": result}

    return {"error": "Invalid action"}