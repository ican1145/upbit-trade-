# app/clients/upbit_client.py

import pyupbit
from app.services.config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY

def get_upbit_client():
    return pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)