import os
import pyupbit
from dotenv import load_dotenv

load_dotenv()

def get_upbit_client():
    access = os.getenv("UPBIT_ACCESS_KEY")
    secret = os.getenv("UPBIT_SECRET_KEY")

    print("[DEBUG] ACCESS EXISTS:", bool(access))
    print("[DEBUG] SECRET EXISTS:", bool(secret))
    print("[DEBUG] ACCESS PREFIX:", access[:6] if access else None)

    if not access or not secret:
        raise Exception("업비트 API 키가 로드되지 않았습니다.")

    return pyupbit.Upbit(access.strip(), secret.strip())