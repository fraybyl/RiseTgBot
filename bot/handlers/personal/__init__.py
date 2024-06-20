__all__ = ("router",)

from aiogram import Router

from .personal_handlers import router as personal_router

router = Router(name=__name__)

router.include_router(personal_router)

