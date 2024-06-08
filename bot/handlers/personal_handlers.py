from aiogram import Router
from aiogram.types import CallbackQuery
from bot.keyboards.personal_keyboard import get_personal_kb
from bot.keyboards.start_keyboard import get_start_kb
from bot.utils.photo_answer_util import edit_message_media
from bot.database import db_requests
from aiogram.utils.deep_linking import create_start_link
from loader import bot


router = Router()

@router.callback_query(lambda query: query.data == "personal")
async def handle_personal_callback(query: CallbackQuery):
    user_id = query.from_user.id
    user_info = await db_requests.get_user_by_telegram_id(user_id)
    link = await create_start_link(bot, user_id, encode=True)
    personalText = (
        f"*Скидка:*  *{user_info.discount_percentage}%*\n"
        f"*Бонусы:*   *{user_info.bonus_points} Rise coins*\n"
        # f"*Сколько вы потратили:* *{round(user.money_spent, 0)} $*\n" ВЫНЕСТИ В ИСТОРИЮ ЗАКАЗОВ
        f"*Реф. ссылка:* `{link}`\n"
        "*Спасибо что вы с нами\\!*\n"
        )
    # Экранирование точки в personalText
    personalText = personalText.replace(".", "\\.")
    
    await edit_message_media(query, "RISE_PERSONAL", get_personal_kb(), personalText)
    
@router.callback_query(lambda query: query.data == "back_personal")
async def handle_back_personal_callback(query: CallbackQuery):
    await edit_message_media(query, "RISE_BACKGROUND", get_start_kb())