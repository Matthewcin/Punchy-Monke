from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.repo_users import get_user
from database.repo_devlogs import add_devlog
from utils.roles import get_user_role
from utils.keyboards import get_back_keyboard

dev_router = Router()

class DevLogState(StatesGroup):
    waiting_for_log = State()

@dev_router.callback_query(F.data == "dev_add_log")
async def cb_add_log(callback: CallbackQuery, state: FSMContext, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    role = get_user_role(callback.from_user.id, user_data)
    
    if role != "dev":
        await callback.answer("Access Denied.", show_alert=True)
        return
        
    await state.set_state(DevLogState.waiting_for_log)
    text = "📝 <b>Send the new Developer Log message:</b>\n\n<i>You can use HTML formatting.</i>"
    await callback.message.edit_text(text, reply_markup=get_back_keyboard())

@dev_router.message(DevLogState.waiting_for_log)
async def process_new_log(message: Message, state: FSMContext, db_pool):
    await add_devlog(db_pool, message.text)
    await state.clear()
    
    text = "✅ <b>DevLog successfully saved!</b>\n\nGo back to the admin panel to view it."
    await message.answer(text, reply_markup=get_back_keyboard())