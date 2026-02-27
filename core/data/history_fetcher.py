from core.utils.http_client import HttpClient


def get_history(symbol="BTCUSDT", interval="1h", limit=10):
    """
    Dummy historical data.
    Returns last `limit` candles.
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}

    data = HttpClient.get(url, params=params)
    if not data:
        return None

    candles = []
    for c in data:
        candles.append(
            {
                "timestamp": c[0],
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[5]),
            }
        )

    return candles
