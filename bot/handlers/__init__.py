__all__ = ("router",)

from aiogram import Router

from .start_handlers import router as start_router
from .shop import router as main_shop_router
from .farmers import router as main_farmers_router
from .personal import router as main_personal_router

router = Router(name=__name__)

router.include_routers(
    start_router,
    main_shop_router,
    main_farmers_router,
    main_personal_router
)