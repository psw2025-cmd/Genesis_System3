import math

def _calc_bs_greeks(spot: float, strike: float, expiry_days: int = 7, option_type: str = "CE", iv: float = 0.22, r: float = 0.06):
    T = max(expiry_days / 365.0, 0.001)
    sigma = max(iv, 0.01)
    try:
        d1 = (math.log(spot / (strike + 1e-6)) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        
        def norm_cdf(x):
            return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
        
        norm_pdf_d1 = math.exp(-0.5 * d1 ** 2) / math.sqrt(2.0 * math.pi)
        
        if option_type.upper() == "CE":
            delta = norm_cdf(d1)
            theta = -(spot * norm_pdf_d1 * sigma) / (2.0 * math.sqrt(T)) - r * strike * math.exp(-r * T) * norm_cdf(d2)
        else:
            delta = norm_cdf(d1) - 1.0
            theta = -(spot * norm_pdf_d1 * sigma) / (2.0 * math.sqrt(T)) + r * strike * math.exp(-r * T) * norm_cdf(-d2)
            
        gamma = norm_pdf_d1 / (spot * sigma * math.sqrt(T) + 1e-6)
        vega = spot * math.sqrt(T) * norm_pdf_d1 * 0.01
        theta_daily = theta / 365.0
        
        return {
            "delta": round(delta, 3),
            "gamma": round(gamma, 5),
            "theta": round(theta_daily, 2),
            "vega": round(vega, 2),
            "iv": round(sigma * 100.0, 1)
        }
    except Exception as e:
        return {"error": str(e)}

print("NIFTY 24000 CE (Spot 23960.60):", _calc_bs_greeks(23960.60, 24000, 7, "CE"))
print("NIFTY 24000 PE (Spot 23960.60):", _calc_bs_greeks(23960.60, 24000, 7, "PE"))
print("RELIANCE 1300 CE (Spot 1300.00):", _calc_bs_greeks(1300.00, 1300, 7, "CE"))
