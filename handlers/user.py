from aiogram import Router, F
from aiogram.types import Message
from database.db import add_user, get_user
from utils.roles import get_user_role
from utils.keyboards import get_main_keyboard
from utils.messages import get_start_message

user_router = Router()

@user_router.message(F.text == "/start")
async def cmd_start(message: Message, db_pool):
    await add_user(db_pool, message.from_user.id)
    user_data = await get_user(db_pool, message.from_user.id)
    
    role = get_user_role(message.from_user.id, user_data)
    keyboard = get_main_keyboard(role)
    text = get_start_message(message.from_user.first_name, message.from_user.id, user_data)
    
    await message.answer(text, reply_markup=keyboard)