# app/services/state.py

profile_state = {}

def _get_bucket(profile: str) -> dict:
    if profile not in profile_state:
        profile_state[profile] = {}
    return profile_state[profile]

def set_buy_state(profile: str, symbol: str, entry_price: float, total_volume: float):
    bucket = _get_bucket(profile)
    bucket[symbol] = {
        "entry_price": entry_price,
        "total_volume": total_volume,
        "tp_order_uuid": None,
        "tp_executed_volume": 0.0
    }

def get_entry_price(profile: str, symbol: str):
    bucket = _get_bucket(profile)
    return bucket.get(symbol, {}).get("entry_price")

def get_total_volume(profile: str, symbol: str):
    bucket = _get_bucket(profile)
    return bucket.get(symbol, {}).get("total_volume", 0.0)