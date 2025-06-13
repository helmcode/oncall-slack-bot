from utils.logger import get_logger
from config.env_vars import config
from services.postgres_storage import PostgresStorage as Storage

logger = get_logger(__name__, level=config.LOG_LEVEL)

def get_current_oncall_text(storage: Storage, intro: str) -> str:
    """Generates the text to show who is on call."""
    try:
        logger.info("Generating oncall text")
        current_latam = storage.get_oncall("LATAM")
        current_eu = storage.get_oncall("EU")

        if not current_latam or not current_eu:
            logger.error("Can't get oncall info")
            return f"{intro}\n\nCan't get oncall info. Use `rotate` to start it."

        return f"""{intro}

*LATAM (8h-17h CO):* <@{current_latam}>
*EU (8h-15h ES):* <@{current_eu}>"""

    except Exception as e:
        logger.error(f"Error getting oncall info: {e}")
        return f"Error getting oncall info: {e}"
