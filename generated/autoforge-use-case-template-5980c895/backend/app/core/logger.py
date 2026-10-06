from loguru import logger

logger.add("logfile.log", rotation="10 MB")
