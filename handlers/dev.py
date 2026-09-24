from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.repo_users import get_user
from database.repo_devlogs import add_devlog
from utils.roles import get_user_role
from utils.keyboards import get_back_keyboard, get_dev_panel_keyboard, get_role_simulation_keyboard, get_main_keyboard
from utils.messages.dev import get_dev_panel_message, get_simulation_message

dev_router = Router()

class DevLogState(StatesGroup):
    waiting_for_log = State()

@dev_router.callback_query(F.data == "menu_dev")
async def cb_dev_panel(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    role = get_user_role(callback.from_user.id, user_data)
    
    if role != "dev":
        await callback.answer("Access Denied.", show_alert=True)
        return
        
    text = get_dev_panel_message()
    keyboard = get_dev_panel_keyboard()
    await callback.message.edit_text(text, reply_markup=keyboard)

@dev_router.callback_query(F.data == "dev_simulate_roles")
async def cb_simulate_roles(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    role = get_user_role(callback.from_user.id, user_data)
    
    if role != "dev":
        await callback.answer("Access Denied.", show_alert=True)
        return
        
    text = get_simulation_message("None Selected")
    keyboard = get_role_simulation_keyboard()
    await callback.message.edit_text(text, reply_markup=keyboard)

@dev_router.callback_query(F.data.startswith("sim_role_"))
async def cb_sim_role_view(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    actual_role = get_user_role(callback.from_user.id, user_data)
    
    if actual_role != "dev":
        await callback.answer("Access Denied.", show_alert=True)
        return
        
    simulated_role = callback.data.replace("sim_role_", "")
    has_checks = True if simulated_role in ["admin", "active_user", "expired_user", "dev"] else False
    
    text = get_simulation_message(simulated_role)
    keyboard = get_main_keyboard(simulated_role, has_checks)
    
    from aiogram.types import InlineKeyboardButton
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🛑 Stop Simulation", callback_data="menu_dev")])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

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
    
    text = "✅ <b>DevLog successfully saved!</b>\n\nGo back to the dev panel to view it."
    await message.answer(text, reply_markup=get_back_keyboard())