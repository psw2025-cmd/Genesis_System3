import requests
from core.utils.logger import logger


class HttpClient:

    @staticmethod
    def get(url: str, params=None, headers=None, timeout=10):
        try:
            logger.info(f"GET {url} params={params}")
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"HTTP GET error: {e}")
            return None
