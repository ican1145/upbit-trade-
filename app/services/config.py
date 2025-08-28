# app/services/config.py

import os
from dotenv import load_dotenv
from threading import RLock

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")

# 유효성 체크
if not UPBIT_ACCESS_KEY or not UPBIT_SECRET_KEY:
    raise ValueError("Upbit API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")

# ===== 자본 관리 설정 =====
INITIAL_CAPITAL = 1_000_000  # 초기 자본 (원) — 프로그램 재시작 시 이 값으로 초기화
FEE_BUY  = 0.0005            # 매수 수수료
FEE_SELL = 0.0005            # 매도 수수료

# 메모리 기반 자본 변수
_CURRENT_CAPITAL = INITIAL_CAPITAL
_cap_lock = RLock()

def get_capital() -> float:
    with _cap_lock:
        return float(_CURRENT_CAPITAL)

def set_capital(v: float):
    global _CURRENT_CAPITAL
    with _cap_lock:
        _CURRENT_CAPITAL = float(v)

def apply_pnl(delta: float):
    """실현손익 delta(원)를 자본에 반영"""
    with _cap_lock:
        set_capital(get_capital() + float(delta))