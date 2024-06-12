from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.database.db_requests import get_all_categories, get_products_by_category, get_product_by_id


#--------------------------START-----------------------
def get_start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Магазин", callback_data="shop"),
                InlineKeyboardButton(text="Фермерам", callback_data="farmers"),
            ],
            [
                InlineKeyboardButton(text="Личный кабинет", callback_data="personal"),
            ],
            [
                InlineKeyboardButton(text="Отзывы", url='https://t.me/risemarket'),
                InlineKeyboardButton(text="Поддержка", url='https://t.me/RiseMarket_support'),
            ]
        ]
    )
    
#--------------------------SHOP-----------------------
async def get_shop_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    
    categories = await get_all_categories()
    
    for category in categories:
        kb.row(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
    
    kb.row(InlineKeyboardButton(text="Назад", callback_data="back_start"))

    return kb.as_markup()

async def get_products_kb(category_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    
    products = await get_products_by_category(category_id)
    
    for product in products:
        kb.row(InlineKeyboardButton(text=product.label, callback_data=f"product_{product.id}"))

    kb.row(InlineKeyboardButton(text="Назад", callback_data="back_shop"))
    
    return kb.as_markup()
    

#--------------------------BUY-ORDER-----------------------
async def get_buy_order_kb(product_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    
    product = await get_product_by_id(product_id)
    
    kb.row(InlineKeyboardButton(text="Купить", callback_data=f"buy_product_{product.id}"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data=f"back_product_{product.category_id}"))
    
    return kb.as_markup()

def get_payment_order_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Оплатить', callback_data='payment_product')
            ],
            [
                InlineKeyboardButton(text='Использовать бонусы', callback_data='bonus_use_product')
            ],
            [
                InlineKeyboardButton(text='Назад', callback_data='back_payment')
            ]
        ]
    )
   
def get_payment_settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Назад', callback_data='back_payment')
            ]
        ]
    )
    
def get_cancel_order_kb(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f"back_order_{product_id}")
            ]
        ]
    )


#--------------------------FARMERS-----------------------
    
def get_farmers_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Подсчитать стратегию", callback_data="strategy"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_start"),
            ]
        ]
    )
    
#--------------------------STRATEGY-----------------------
def get_strategy_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard= [
            [
                InlineKeyboardButton(text="Агрессивная стратегия", callback_data="aggressive_strategy")
            ],
            [
                InlineKeyboardButton(text="Умеренная стратегия", callback_data="moderate_strategy"),
            ],
            [
                InlineKeyboardButton(text="Консервативная стратегия", callback_data="conservative_strategy"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_farmers"),
            ]
        ]
    )

def get_cancel_strategy_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard= [
            [
                InlineKeyboardButton(text='В начало', callback_data='back_farmers')
            ],
            [
                InlineKeyboardButton(text='Назад', callback_data="back_strategy")
            ]
        ]
    )
    
#--------------------------PERSONAL-----------------------
    
def get_personal_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data="back_start"),
            ]
        ]
    )
    


