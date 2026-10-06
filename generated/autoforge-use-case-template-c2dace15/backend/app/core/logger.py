from loguru import logger

# Configure logger here if needed
logger.add("logs/app.log", rotation="1 week", retention="1 month", compression="zip")
