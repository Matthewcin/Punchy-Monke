from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.repo_users import get_user, get_all_users
from database.repo_devlogs import add_devlog
from database.repo_settings import get_setting, set_setting
from utils.roles import get_user_role
from utils.keyboards import get_back_keyboard, get_dev_panel_keyboard, get_maintenance_keyboard, get_maintenance_confirm_keyboard
from utils.messages.dev import get_dev_panel_message, get_maintenance_message, get_maintenance_confirm_message

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

@dev_router.callback_query(F.data == "dev_maintenance")
async def cb_maintenance_menu(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    if get_user_role(callback.from_user.id, user_data) != "dev":
        return
        
    maint_status = await get_setting(db_pool, 'maintenance_mode')
    is_active = maint_status == 'true'
    
    text = get_maintenance_message(is_active)
    keyboard = get_maintenance_keyboard(is_active)
    await callback.message.edit_text(text, reply_markup=keyboard)

@dev_router.callback_query(F.data == "dev_maint_toggle")
async def cb_maintenance_toggle(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    if get_user_role(callback.from_user.id, user_data) != "dev":
        return
        
    maint_status = await get_setting(db_pool, 'maintenance_mode')
    is_active = maint_status == 'true'
    
    if is_active:
        await set_setting(db_pool, 'maintenance_mode', 'false')
        text = get_maintenance_message(False)
        keyboard = get_maintenance_keyboard(False)
        await callback.message.edit_text(text, reply_markup=keyboard)
    else:
        text = get_maintenance_confirm_message()
        keyboard = get_maintenance_confirm_keyboard()
        await callback.message.edit_text(text, reply_markup=keyboard)

@dev_router.callback_query(F.data == "dev_maint_confirm_yes")
async def cb_maintenance_confirm_yes(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    if get_user_role(callback.from_user.id, user_data) != "dev":
        return
        
    await set_setting(db_pool, 'maintenance_mode', 'true')
    
    users = await get_all_users(db_pool)
    for u in users:
        try:
            await callback.bot.send_message(
                u['telegram_id'], 
                "🚧 <b>Maintenance Break</b>\n\nThe bot is currently undergoing maintenance and will be back shortly."
            )
        except Exception:
            pass
            
    text = get_maintenance_message(True)
    keyboard = get_maintenance_keyboard(True)
    await callback.message.edit_text(text, reply_markup=keyboard)

@dev_router.callback_query(F.data == "dev_maint_confirm_no")
async def cb_maintenance_confirm_no(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    if get_user_role(callback.from_user.id, user_data) != "dev":
        return
        
    text = get_maintenance_message(False)
    keyboard = get_maintenance_keyboard(False)
    await callback.message.edit_text(text, reply_markup=keyboard)

@dev_router.callback_query(F.data == "dev_add_log")
async def cb_add_log(callback: CallbackQuery, state: FSMContext, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    if get_user_role(callback.from_user.id, user_data) != "dev":
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