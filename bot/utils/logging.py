import logging
from loguru import logger
from bot.core.config import settings


class InterceptHandler(logging.Handler):
    """
    Обработчик для перехвата и логирования сообщений из стандартного логгера в Loguru.

    Methods:
        emit(record):
            Перехватывает сообщение из стандартного логгера и передает его в Loguru.
    """

    def emit(self, record):
        """
        Перехватывает и логирует сообщение из стандартного логгера.

        Args:
            record (LogRecord): Запись логгера с информацией о сообщении.
        """
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


if settings.DEBUG:
    log_level = logging.DEBUG
    logger_level = "DEBUG"
else:
    log_level = logging.WARNING
    logger_level = "WARNING"

logging.basicConfig(handlers=[InterceptHandler()], level=log_level)
logger.add(
    "logs/telegram_bot.log",
    level=logger_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}",
    rotation="100 KB",
    compression="zip",
)
