__all__ = ("router",)

from aiogram import Router

from .farmers_handlers import router as farmers_router
from .inventory_handlers import router as inventory_router
from .strategy_handlers import router as strategy_router

router = Router(name=__name__)

router.include_router(farmers_router)
router.include_router(strategy_router)
router.include_router(inventory_router)
