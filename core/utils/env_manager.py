from core.utils.config_loader import ensure_config
from core.utils.logger import logger


class EnvManager:

    def __init__(self):
        self.config = ensure_config()
        logger.info("Environment Manager Loaded")

    def is_live(self):
        return self.config.get("live_mode", False)

    def get_market(self):
        return self.config.get("market", "NSE")

    def set_live_mode(self, status: bool):
        self.config["live_mode"] = status
        logger.info(f"Live Mode set to {status}")

    def get_update_interval(self):
        return self.config.get("update_interval_sec", 5)


env = EnvManager()
