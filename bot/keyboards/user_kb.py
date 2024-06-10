from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


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
def get_shop_kb() -> InlineKeyboardMarkup: 
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Аккаунты LIMIT", callback_data="limit_accounts"),
            ],
            [
                InlineKeyboardButton(text="Steam Gift Code", callback_data="steam_gift_code"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_start"),
            ]
        ]
    )
    
#--------------------------LIMIT-ACC-----------------------
def get_limit_acc_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="NON-SDA", callback_data="buy_sda_non")
            ],
            [
                InlineKeyboardButton(text="SDA", callback_data="buy_sda")
            ],
            [
                InlineKeyboardButton(text="SDA-2LVL", callback_data="buy_sda_2lvl")
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_shop")
            ]
        ]
    )
    
#--------------------------GIFT-CODE-----------------------
def get_gift_code_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="GIFT-5", callback_data="buy_gift_5")
            ],
            [
                InlineKeyboardButton(text="GIFT-10", callback_data="buy_gift_10")
            ],
            [
                InlineKeyboardButton(text="GIFT-15", callback_data="buy_gift_15")
            ],
            [
                InlineKeyboardButton(text="GIFT-20", callback_data="buy_gift_20")
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_shop")
            ]
        ]
    )
       

#--------------------------BUY-ORDER-----------------------
def get_buy_order_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Купить", callback_data="buy_product")
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_categories")
            ]
        ]
    )

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
                InlineKeyboardButton(text='Назад', callback_data='back_order')
            ]
        ]
    )

def get_cancel_order_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data="back_order")
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
    


