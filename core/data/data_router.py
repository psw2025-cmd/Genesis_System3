from core.data.live_fetcher import get_live_price
from core.data.history_fetcher import get_history
from core.data.storage_manager import save_json_snapshot
from core.utils.logger import logger


def fetch_and_store_live(symbol="BTCUSDT"):
    logger.info(f"Fetching live price for {symbol}")
    data = get_live_price(symbol)
    if not data:
        logger.error("Live fetch failed")
        return None

    path = save_json_snapshot(data, f"LIVE_{symbol}")
    logger.info(f"Live snapshot stored at: {path}")
    return path


def fetch_and_store_history(symbol="BTCUSDT", interval="1h", limit=10):
    logger.info(f"Fetching history for {symbol}")
    data = get_history(symbol, interval, limit)
    if not data:
        logger.error("History fetch failed")
        return None

    path = save_json_snapshot({"candles": data}, f"HIST_{symbol}")
    logger.info(f"History snapshot stored at: {path}")
    return path
