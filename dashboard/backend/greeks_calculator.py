"""Calculate Greeks."""
import math
from datetime import datetime

def calculate_iv(spot, strike, price, expiry_days, option_type='CE', rate=0.05):
    try:
        T = max(expiry_days / 365, 0.001)
        if option_type == 'CE':
            intrinsic = max(spot - strike, 0)
            time_value = max(price - intrinsic, 0)
            if time_value <= 0: return 0.01
            iv = (time_value * math.sqrt(math.pi / (2 * T))) / (spot + 0.001)
            return min(max(iv, 0.01), 3.0)
        else:
            intrinsic = max(strike - spot, 0)
            time_value = max(price - intrinsic, 0)
            if time_value <= 0: return 0.01
            iv = (time_value * math.sqrt(math.pi / (2 * T))) / (spot + 0.001)
            return min(max(iv, 0.01), 3.0)
    except: return 0.20

def calculate_delta(spot, strike, expiry_days, option_type='CE', iv=0.20):
    try:
        T = max(expiry_days / 365, 0.001)
        d1 = (math.log(spot / (strike + 0.001)) + 0.5 * iv**2 * T) / (iv * math.sqrt(T) + 0.001)
        return 1 / (1 + math.exp(-d1)) if option_type == 'CE' else (1 / (1 + math.exp(-d1))) - 1
    except: return 0.5

def calculate_gamma(spot, strike, expiry_days, iv=0.20):
    try:
        T = max(expiry_days / 365, 0.001)
        d1 = (math.log(spot / (strike + 0.001)) + 0.5 * iv**2 * T) / (iv * math.sqrt(T) + 0.001)
        n_d1 = math.exp(-0.5 * d1**2) / math.sqrt(2 * math.pi)
        return n_d1 / (spot * iv * math.sqrt(T) + 0.001)
    except: return 0.01

def enrich_contract_with_greeks(contract):
    try:
        if contract.get("iv", 0) > 0: return contract
        spot = contract.get("spot_price", 0)
        strike = contract.get("strike", 0)
        ltp = contract.get("ltp", 0)
        if not all([spot > 0, strike > 0, ltp > 0]): return contract
        expiry_days = 7
        try:
            exp_date = datetime.strptime(str(contract.get("expiry_date", "")), "%Y-%m-%d")
            expiry_days = max((exp_date - datetime.now()).days, 0)
        except: pass
        option_type = contract.get("option_type", "CE")
        iv = calculate_iv(spot, strike, ltp, expiry_days, option_type)
        delta = calculate_delta(spot, strike, expiry_days, option_type, iv)
        gamma = calculate_gamma(spot, strike, expiry_days, iv)
        contract["iv"] = round(iv, 4)
        contract["delta"] = round(delta, 4)
        contract["gamma"] = round(gamma, 6)
        contract["vega"] = round(iv * spot * 0.01, 4)
        contract["theta"] = round(-ltp / max(expiry_days, 1), 4)
        return contract
    except: return contract

def enrich_contracts_list(contracts):
    return [enrich_contract_with_greeks(c) for c in contracts]
