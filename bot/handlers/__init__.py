__all__ = ("router",)

from aiogram import Router

from .start_handlers import router as start_router
from .shop import router as shop_router
from .personal import router as personal_router
from .farmers import router as farmers_router

router = Router(name=__name__)

router.include_routers(
    start_router,
    shop_router,
    personal_router,
    farmers_router)
