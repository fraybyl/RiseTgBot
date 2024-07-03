from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .ban_statistics import ban_statistics_schedule
from .providers_items_update import providers_items_update


def start_schedulers() -> None:
    """
    Инициализация планировщика задач
    """
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(ban_statistics_schedule, IntervalTrigger(hours=1))
    scheduler.add_job(providers_items_update, IntervalTrigger(seconds=10))
    scheduler.start()
