from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .ban_statistics import ban_statistics_schedule


def start_schedulers() -> None:
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(ban_statistics_schedule, IntervalTrigger(hours=1))

    scheduler.start()
