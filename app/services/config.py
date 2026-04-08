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
INITIAL_CAPITAL = 200_000  # 초기 자본 (원) — 프로그램 재시작 시 이 값으로 초기화
FEE_BUY  = 0.0005            # 매수 수수료
FEE_SELL = 0.0005            # 매도 수수료

# webhook1(복리) 기반 자본 변수
_CURRENT_CAPITAL = INITIAL_CAPITAL
_cap_lock = RLock()

PROFILE_COMPOUND = "webhook1"
PROFILE_FIXED = "webhook2"

def get_capital(profile: str = PROFILE_COMPOUND) -> float:
    """
    - webhook1: 복리 자본(_CURRENT_CAPITAL)
    - webhook2: 고정 자본(INITIAL_CAPITAL)
    """
    if profile == PROFILE_FIXED:
        return float(INITIAL_CAPITAL)

    with _cap_lock:
        return float(_CURRENT_CAPITAL)

def set_capital(v: float):
    global _CURRENT_CAPITAL
    with _cap_lock:
        _CURRENT_CAPITAL = float(v)

def apply_pnl(delta: float, profile: str = PROFILE_COMPOUND):
    """
    - webhook1만 복리 반영
    - webhook2는 반영하지 않음(고정 자본)
    """
    if profile == PROFILE_FIXED:
        return

    with _cap_lock:
        set_capital(get_capital(PROFILE_COMPOUND) + float(delta))