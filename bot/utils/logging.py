from loguru import logger
import logging


class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=0)
logger.add(
    "logs/telegram_bot.log",
    level="DEBUG",
    format="{time} | {level} | {module}:{function}:{line} | {message}",
    rotation="100 KB",
    compression="zip",
)
