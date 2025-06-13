import os
from utils.logger import get_logger

logger = get_logger("env_vars", level=os.environ.get("LOG_LEVEL", "INFO"))

class AppConfig:
    """Loads and stores environment variables for the application."""
    SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
    SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
    SUPPORT_CHANNEL = os.environ.get("SUPPORT_CHANNEL", "#tests")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

    required_vars = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        logger.error(f"❌ Env vars missing: {missing_vars}")
        logger.info("\n🔧 Set env vars:")
        logger.info("export SLACK_BOT_TOKEN='xoxb-bot-token'")
        logger.info("export SLACK_APP_TOKEN='xapp-app-token'")
        logger.info("export LOG_LEVEL='DEBUG'")
        raise Exception("❌ Env vars missing")

config = AppConfig()
