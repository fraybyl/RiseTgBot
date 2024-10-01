__all__ = ("router",)

from aiogram import Router

from .farmers import router as farmers_router
from .message_distributor_handlers import router as message_distributor_handlers_router
from .personal import router as personal_router
from .shop import router as shop_router
from .start_handlers import router as start_router
from .admin.admin_handlers import router as admins_router
from .admin.mailing_list import router as mailing_router

router = Router(name=__name__)

router.include_routers(
    start_router,
    shop_router,
    personal_router,
    farmers_router,
    admins_router,
    mailing_router,
    message_distributor_handlers_router)
