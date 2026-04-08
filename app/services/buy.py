# app/services/buy.py

from app.clients.upbit_client import get_upbit_client
from app.services.state import set_buy_state
from app.services.config import get_capital
import pyupbit
import math
import time


def _round_down(value: float, decimals: int = 8) -> float:
    return math.floor(value * (10 ** decimals)) / (10 ** decimals)


def execute_buy(symbol: str, profile: str = "webhook1"):
    """
    - profile별 자본(get_capital(profile)) 기준으로 예산(amount) 계산
    - 중복 진입 방지: 평가금액 ≥ 1,000원이면 스킵
    - 시장가 매수 후 평균 체결가와 총 체결수량만 state에 저장(profile별)
    """
    try:
        upbit = get_upbit_client()

        # 1) 자본 기반 예산 산출 (webhook2는 항상 INITIAL_CAPITAL)
        capital = int(get_capital(profile))
        if capital < 5100:
            raise Exception("자본이 부족합니다(최소 5,100원 이상 필요).")

        balances = upbit.get_balances()
        print(f"[DEBUG] get_balances() = {balances}")

        krw = upbit.get_balance("KRW")
        print(f"[DEBUG] get_balance('KRW') = {krw}")
        if krw is None:
            raise Exception("KRW 잔고 조회 실패")
        amount = min(capital, int(float(krw) * 0.995))
        if amount < 5100:
            raise Exception("실제 잔고 기준 주문금액이 부족합니다.")

        # 3) 중복 진입 방지
        balance_volume = upbit.get_balance(symbol)  # 예: "KRW-SOL"
        if balance_volume and float(balance_volume) > 0:
            current_price = pyupbit.get_current_price(symbol)
            if current_price and float(balance_volume) * float(current_price) >= 1000:
                print(f"[SKIPPED] {symbol} 이미 보유 중 (평가액 ≥ 1,000원)")
                return {"status": "skipped"}

        # 4) 시장가 매수
        result = upbit.buy_market_order(symbol, amount)
        print(f"[BUY] ({profile}) {symbol} 시장가 매수 요청: {result}")

        uuid = result.get("uuid") if result else None
        if not uuid:
            raise Exception("매수 응답에 UUID가 없습니다.")

        # 5) 체결 정보 조회 → 평균 체결가/총 체결수량 계산
        time.sleep(0.5)
        order = upbit.get_order(uuid)
        trades = order.get("trades", [])
        if not trades or float(trades[0].get("volume", 0)) == 0:
            raise Exception("체결 정보 부족: trades 없음 또는 체결 수량 0")

        total_cost = 0.0
        total_vol = 0.0
        for t in trades:
            p = float(t["price"])
            v = float(t["volume"])
            total_cost += p * v
            total_vol  += v

        if total_vol <= 0:
            raise Exception("체결 수량이 0입니다.")

        entry_price = total_cost / total_vol
        total_volume = _round_down(total_vol)

        # 6) 상태 저장 (profile별)
        set_buy_state(profile, symbol, entry_price, total_volume)

        print(f"[BUY DONE] ({profile}) {symbol} avg={entry_price}, vol={total_volume}")
        return {"status": "ok", "entry_price": entry_price, "volume": total_volume}

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[BUY ERROR] ({profile}) {symbol}: {e}")
        return {"status": "error", "message": str(e)}