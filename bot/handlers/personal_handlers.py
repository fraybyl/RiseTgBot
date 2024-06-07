from aiogram import Router
from aiogram.types import CallbackQuery
from bot.keyboards.personal_keyboard import get_personal_kb
from bot.keyboards.start_keyboard import get_start_kb
from bot.utils.photo_answer_util import edit_message_media

router = Router()

@router.callback_query(lambda query: query.data == "personal")
async def handle_personal_callback(query: CallbackQuery):
    #user = await dbRequests.get_user_by_telegram_id(callback_query.from_user.id)
    #link = await create_start_link(Bot, user.referral_code)

    personalText = (
        f"*Скидка:*  *%*\n"
        f"*Бонусы:*   *Rise coins*\n"
        # f"*Сколько вы потратили:* *{round(user.money_spent, 0)} $*\n" ВЫНЕСТИ В ИСТОРИЮ ЗАКАЗОВ
        f"*Реферальный код:* ``\n"
        "*Спасибо что вы с нами\\!*\n"
        )
    # Экранирование точки в personalText
    personalText = personalText.replace(".", "\\.")
    
    await edit_message_media(query, "RISE_PERSONAL", get_personal_kb(), personalText)
    
@router.callback_query(lambda query: query.data == "back_personal")
async def handle_back_personal_callback(query: CallbackQuery):
    await edit_message_media(query, "RISE_BACKGROUND", get_start_kb())