from aiogram import Router, F
from aiogram.types import Message
from database.repo_users import add_user, get_user
from database.repo_logs import get_user_checks_count
from database.repo_orders import get_user_order_status
from utils.roles import get_user_role
from utils.keyboards import get_main_keyboard
from utils.messages.start import get_start_message

user_router = Router()

@user_router.message(F.text == "/start")
async def cmd_start(message: Message, db_pool):
    await add_user(db_pool, message.from_user.id)
    user_data = await get_user(db_pool, message.from_user.id)
    checks_count = await get_user_checks_count(db_pool, message.from_user.id)
    
    has_checks = checks_count > 0
    role = get_user_role(message.from_user.id, user_data)
    orders_emoji = await get_user_order_status(db_pool, message.from_user.id)
    
    keyboard = get_main_keyboard(role, has_checks, orders_emoji)
    text = get_start_message(message.from_user.first_name, message.from_user.id, user_data)
    
    await message.answer(text, reply_markup=keyboard)