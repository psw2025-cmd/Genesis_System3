from core.utils.http_client import HttpClient


def get_live_price(symbol="BTCUSDT"):
    """
    Dummy live price using Binance public API.
    Works without API key.
    """
    url = "https://api.binance.com/api/v3/ticker/price"
    data = HttpClient.get(url, params={"symbol": symbol})

    if not data or "price" not in data:
        return None

    return {"symbol": symbol, "price": float(data["price"])}
