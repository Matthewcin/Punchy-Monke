from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.repo_users import get_user
from database.repo_logs import get_user_checks_count
from utils.keyboards import get_back_keyboard
from utils.messages.profile import get_profile_message

profile_router = Router()

@profile_router.callback_query(F.data == "menu_profile")
async def cb_profile(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    checks_count = await get_user_checks_count(db_pool, callback.from_user.id)
    
    text = get_profile_message(callback.from_user.first_name, callback.from_user.id, user_data, checks_count)
    keyboard = get_back_keyboard()
    
    await callback.message.edit_text(text, reply_markup=keyboard)