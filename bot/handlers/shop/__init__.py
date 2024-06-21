__all__ = ("router",)

from aiogram import Router

from .shop_handlers import router as shop_router
from .categories_handlers import router as categories_router
from .product_handlers import router as product_router
from .order_handlers import router as order_router


router = Router(name=__name__)

router.include_router(shop_router)
router.include_router(categories_router)
router.include_router(product_router)
router.include_router(order_router)
