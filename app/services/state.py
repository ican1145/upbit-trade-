# app/services/state.py

symbol_state = {}

def set_buy_state(symbol: str, entry_price: float, total_volume: float):
    symbol_state[symbol] = {
        "entry_price": entry_price,
        "total_volume": total_volume,
        "tp_order_uuid": None,
        "tp_executed_volume": 0.0
    }

def set_tp_order_uuid(symbol: str, uuid: str):
    if symbol in symbol_state:
        symbol_state[symbol]["tp_order_uuid"] = uuid

def set_tp_executed_volume(symbol: str, volume: float):
    if symbol in symbol_state:
        symbol_state[symbol]["tp_executed_volume"] = volume

def get_entry_price(symbol: str):
    return symbol_state.get(symbol, {}).get("entry_price")

def get_total_volume(symbol: str):
    return symbol_state.get(symbol, {}).get("total_volume", 0.0)

def get_tp_order_uuid(symbol: str):
    return symbol_state.get(symbol, {}).get("tp_order_uuid")

def get_tp_executed_volume(symbol: str):
    return symbol_state.get(symbol, {}).get("tp_executed_volume", 0.0)