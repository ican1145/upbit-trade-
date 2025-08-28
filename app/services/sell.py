# app/services/sell.py

from app.clients.upbit_client import get_upbit_client
from app.services.state import get_total_volume, get_entry_price
from app.services.config import apply_pnl, FEE_BUY, FEE_SELL
import math
import time


def _round_down(value: float, decimals: int = 8) -> float:
    return math.floor(value * (10 ** decimals)) / (10 ** decimals)


def _avg_price_from_trades(trades):
    """체결 리스트에서 평균 체결가와 총 체결수량을 계산"""
    if not trades:
        return None, 0.0
    cost, vol = 0.0, 0.0
    for t in trades:
        p = float(t["price"])
        v = float(t["volume"])
        cost += p * v
        vol += v
    if vol <= 0:
        return None, 0.0
    return cost / vol, vol


def execute_sell_all(symbol: str):
    """
    - state에 저장된 진입가/보유수량 기반으로 실현손익 계산
    - 시장가로 전량 매도 시도 (부분 체결 시 체결분만 PnL 반영)
    - PnL = (매도수익*(1-FEE_SELL)) - (매수원가*(1+FEE_BUY))
    - apply_pnl()로 자본 업데이트 → 다음 매매에 복리 반영
    """
    try:
        upbit = get_upbit_client()

        total_volume = float(get_total_volume(symbol))
        if total_volume <= 0:
            print(f"[SELL] {symbol} 보유 수량 없음")
            return None

        entry_price = float(get_entry_price(symbol))
        if entry_price <= 0:
            raise Exception("진입가가 유효하지 않습니다.")

        # 1) 시장가 전량 매도
        sell_res = upbit.sell_market_order(symbol, total_volume)
        print(f"[SELL] {symbol} 시장가 청산 요청: vol={total_volume}, res={sell_res}")

        uuid = sell_res.get("uuid") if sell_res else None
        if not uuid:
            raise Exception("매도 응답에 UUID가 없습니다.")

        # 2) 체결 상세 조회
        time.sleep(0.5)
        order = upbit.get_order(uuid)
        trades = order.get("trades", [])
        avg_sell, executed_vol = _avg_price_from_trades(trades)
        executed_vol = _round_down(executed_vol)

        if executed_vol <= 0 or avg_sell is None:
            raise Exception("매도 체결 정보가 없습니다.")

        # 3) 실현손익 계산 (부분 체결도 안전하게 처리)
        buy_cost     = entry_price * executed_vol * (1.0 + FEE_BUY)
        sell_revenue = (avg_sell   * executed_vol) * (1.0 - FEE_SELL)
        pnl = sell_revenue - buy_cost

        # 4) 자본 업데이트 (복리)
        apply_pnl(pnl)

        print(f"[PNL] {symbol} realized={pnl:.2f}원  "
              f"(buy_cost={buy_cost:.2f}, sell_revenue={sell_revenue:.2f}, "
              f"exec_vol={executed_vol}, avg_sell={avg_sell})")

        return {
            "pnl": pnl,
            "executed_volume": executed_vol,
            "avg_sell_price": avg_sell
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[SELL ERROR] {symbol}: {e}")
        return None