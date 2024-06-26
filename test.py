from enum import Enum

from aiogram.filters.callback_data import CallbackData


class ShopActions(Enum):
    SHOP = "shop"
    BACK_SHOP = "back_shop"
    CATEGORY = "category"
    PRODUCT = "product"
    BACK_PRODUCT = "back_product"
    BUY_PRODUCT = "buy_product"
    BACK_ORDER = "back_order"
    PAYMENT_PRODUCT = "payment_product"
    BONUS_USE_PRODUCT = "bonus_use_product"
    BACK_PAYMENT = "back_payment"

class ShopCallbackData(CallbackData, prefix="shop"):
    action: ShopActions
    id: int = None

from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.database.db_requests import get_all_categories, get_products_by_category


async def get_shop_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    categories = await get_all_categories()

    for category in categories:
        kb.row(InlineKeyboardButton(text=category.name, callback_data=ShopCallbackData(action=ShopActions.CATEGORY, id=category.id).pack()))

    kb.row(InlineKeyboardButton(text="Назад", callback_data=ShopCallbackData(action=ShopActions.BACK_SHOP).pack()))

    return kb.as_markup()

async def get_products_kb(category_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    products = await get_products_by_category(category_id)

    for product in products:
        kb.row(InlineKeyboardButton(text=product.label, callback_data=ShopCallbackData(action=ShopActions.PRODUCT, id=product.id).pack()))

    kb.row(InlineKeyboardButton(text="Назад", callback_data=ShopCallbackData(action=ShopActions.BACK_SHOP).pack()))

    return kb.as_markup()

async def get_product_desc_kb(product_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    product = await get_product_by_id(product_id)

    kb.row(InlineKeyboardButton(text="Купить", callback_data=ShopCallbackData(action=ShopActions.BUY_PRODUCT, id=product.id).pack()))
    kb.row(InlineKeyboardButton(text="Назад", callback_data=ShopCallbackData(action=ShopActions.BACK_PRODUCT, id=product.category_id).pack()))

    return kb.as_markup()

def get_payment_order_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Оплатить', callback_data=ShopCallbackData(action=ShopActions.PAYMENT_PRODUCT).pack())],
            [InlineKeyboardButton(text='Использовать бонусы', callback_data=ShopCallbackData(action=ShopActions.BONUS_USE_PRODUCT).pack())],
            [InlineKeyboardButton(text='Назад', callback_data=ShopCallbackData(action=ShopActions.BACK_PAYMENT).pack())]
        ]
    )

def get_payment_settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data=ShopCallbackData(action=ShopActions.BACK_PAYMENT).pack())]
        ]
    )

def get_cancel_order_kb(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data=ShopCallbackData(action=ShopActions.BACK_ORDER, id=product_id).pack())]
        ]
    )

from aiogram import Router
from aiogram.types import CallbackQuery
from bot.utils.edit_media import edit_message_media
from bot.keyboards.shop_keyboards import get_shop_kb, get_products_kb, get_product_desc_kb, get_cancel_order_kb, \
    get_payment_settings_kb
from bot.database.db_requests import get_category_by_id, get_product_by_id
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization

router = Router(name=__name__)

@router.callback_query(ShopCallbackData.filter(F.action == ShopActions.SHOP))
async def handle_shop(query: CallbackQuery, callback_data: ShopCallbackData):
    await edit_message_media(query, 'RISE_SHOP', await get_shop_kb())

@router.callback_query(ShopCallbackData.filter(F.action == ShopActions.BACK_SHOP))
async def handle_back_shop(query: CallbackQuery, callback_data: ShopCallbackData):
    await edit_message_media(query, 'RISE_SHOP', await get_shop_kb())

@router.callback_query(ShopCallbackData.filter(F.action == ShopActions.CATEGORY))
async def handle_products_category(query: CallbackQuery, callback_data: ShopCallbackData):
    category = await get_category_by_id(callback_data.id)
    await edit_message_media(query, category.photo_filename, await get_products_kb(callback_data.id))

@router.callback_query(ShopCallbackData.filter(F.action == ShopActions.PRODUCT))
async def handle_product(query: CallbackQuery, callback_data: ShopCallbackData):
    product = await get_product_by_id(callback_data.id)
    await edit_message_media(query, product.photo_filename, await get_product_desc_kb(callback_data.id), caption=product.label)

@router.callback_query(ShopCallbackData.filter(F.action == ShopActions.BACK_PRODUCT))
async def handle_back_products(query: CallbackQuery, callback_data: ShopCallbackData, state: FSMContext):
    category = await get_category_by_id(callback_data.id)
    await edit_message_media(query, category.photo_filename, await get_products_kb(callback_data.id))

@router.callback_query(ShopCallbackData.filter(F.action == ShopActions.BUY_PRODUCT))
async def handle_buy_product(query: CallbackQuery, callback_data: ShopCallbackData, state: FSMContext, l10n: FluentLocalization):
    product = await get_product_by_id(callback_data.id)
    user = await get_user_by_telegram_id(query.from_user.id)

    minimal_price = await config_json.get_config_value('minimal_price')
    min_quantity = calculate_quantity(product.price, user.discount_percentage, minimal_price)

    message = await query.message.edit_caption(
        caption=l10n.format_value('product-quantity', {'quantity': product.quantity, 'min': min_quantity}),
        reply_markup=get_cancel_order_kb(callback_data.id))

    await state.set_state(OrderStates.WAITING_PRODUCT_QUANTITY)
    await state.update_data(min_quantity=min_quantity)
    await state.update_data(product=product.as_dict)
    await state.update_data(user=user.as_dict)
    await state.update_data(minimal_price=minimal_price)
    await state.update_data(message_id=message.message_id)

@router.callback_query(ShopCallbackData.filter(F.action == ShopActions.BACK_ORDER))
async def handle_back_products(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product = data.get('product')
    await state.clear()
    await edit_message_media(query, product.photo_filename, await get_product_desc_kb(product['id']), caption=product.label)

@router.callback_query(ShopCallbackData.filter(F.action == ShopActions.PAYMENT_PRODUCT))
async def handle_payment_product(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quantity_product = data.get('quantity_product')
    quantity_bonus = data.get('quantity_bonus')
    await query.message.edit_caption(caption=f"Продукта {quantity_product}\n Бонусов: {quantity_bonus or 0}", reply_markup=get_payment_settings_kb())
    await state.set_state(OrderStates.WAITING_PAYMENT)

@router.callback_query(ShopCallbackData.filter(F.action == ShopActions.BONUS_USE_PRODUCT))
async def handle_bonus_use(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quantity_product = data.get('quantity_product')
    product = data.get('product')
    user = data.get('user')
    minimal_price = data.get('minimal_price')

    await state.set_state(OrderStates.WAITING_BONUS_QUANTITY)
    if user['bonus_points'] > 0:
        max_bonus = calculate_max_bonus(product['price'] * quantity_product, user['discount_percentage'], minimal_price)

        await query.message.edit_caption(
            caption=f"Введите количество не больше {min(max_bonus, user['bonus_points']):.0f}",
            reply_markup=get_payment_settings_kb())

        await state.update_data(max_bonus=min(max_bonus, user['bonus_points']))
    else:
        await query.message.edit_caption(caption=f"У вас нет бонусов для использования", reply_markup=get_payment_settings_kb())
        await state.update_data(max_bonus=-1)

@router.callback_query(ShopCallbackData.filter(F.action == ShopActions.BACK_PAYMENT))
async def handle_back_payment(query: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    data = await state.get_data()
    current_state = await state.get_state()

    if current_state is None:
        product = data.get('product')
        min_quantity = data.get('min_quantity')
        await query.message.edit_caption(caption=f"Введите количество не меньше {min_quantity}", reply_markup=get_cancel_order_kb(product['id']))
        await state.update_data(quantity_product=None)
        await state.set_state(OrderStates.WAITING_PRODUCT_QUANTITY)
    elif current_state == OrderStates.WAITING_BONUS_QUANTITY:
        quantity_product = data.get('quantity_product')
        await query.message.edit_caption(caption=f"Продукта {quantity_product}\n Бонусов: 0", reply_markup=get_payment_settings_kb())
        await state.set_state(OrderStates.WAITING_PAYMENT)
