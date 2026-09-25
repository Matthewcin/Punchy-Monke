import math
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.repo_users import get_user, get_broadcast_users
from database.repo_devlogs import get_devlog_dates_count, get_devlog_dates_paginated, get_devlogs_by_date
from utils.roles import get_user_role
from utils.keyboards import get_admin_panel_keyboard, get_devlog_dates_keyboard, get_devlog_message_keyboard, get_role_simulation_keyboard, get_main_keyboard, get_broadcast_menu_keyboard, get_broadcast_confirm_keyboard
from utils.messages.admin import get_admin_panel_message, get_devlog_dates_message, get_devlog_content_message, get_simulation_message, get_broadcast_prompt_message, get_broadcast_confirm_message

admin_router = Router()

class BroadcastState(StatesGroup):
    waiting_for_message = State()
    confirm_broadcast = State()

@admin_router.callback_query(F.data == "menu_admin")
async def cb_admin_panel(callback: CallbackQuery, db_pool, state: FSMContext):
    await state.clear()
    user_data = await get_user(db_pool, callback.from_user.id)
    role = get_user_role(callback.from_user.id, user_data)
    
    if role not in ["admin", "dev"]:
        await callback.answer("Access Denied.", show_alert=True)
        return
        
    text = get_admin_panel_message()
    keyboard = get_admin_panel_keyboard(role)
    await callback.message.edit_text(text, reply_markup=keyboard)

@admin_router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    role = get_user_role(callback.from_user.id, user_data)
    
    if role not in ["admin", "dev"]:
        return
        
    text = "📢 <b>Broadcast Menu</b>\n\nSelect the target audience for your message:"
    keyboard = get_broadcast_menu_keyboard()
    await callback.message.edit_text(text, reply_markup=keyboard)

@admin_router.callback_query(F.data.startswith("bc_target_"))
async def cb_broadcast_target(callback: CallbackQuery, db_pool, state: FSMContext):
    target_type = callback.data.replace("bc_target_", "")
    users = await get_broadcast_users(db_pool, target_type)
    counter = len(users)
    
    await state.update_data(target_type=target_type, counter=counter)
    await state.set_state(BroadcastState.waiting_for_message)
    
    text = get_broadcast_prompt_message(target_type, counter)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="admin_broadcast")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@admin_router.message(BroadcastState.waiting_for_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    await state.update_data(broadcast_text=message.html_text)
    data = await state.get_data()
    
    text = get_broadcast_confirm_message(data['target_type'], data['counter'])
    text += f"\n\n<b>Message Preview:</b>\n{data['broadcast_text']}"
    
    await state.set_state(BroadcastState.confirm_broadcast)
    keyboard = get_broadcast_confirm_keyboard()
    await message.answer(text, reply_markup=keyboard)

@admin_router.callback_query(BroadcastState.confirm_broadcast, F.data == "bc_confirm_yes")
async def cb_broadcast_send(callback: CallbackQuery, db_pool, state: FSMContext):
    data = await state.get_data()
    target_type = data['target_type']
    message_text = data['broadcast_text']
    
    sender_name = callback.from_user.first_name
    final_message = f"{message_text}\n\n<i>Broadcast Sent by: {sender_name}</i>"
    
    await callback.message.edit_text("⏳ Broadcasting message, please wait...")
    
    users = await get_broadcast_users(db_pool, target_type)
    success = 0
    failed = 0
    
    for u in users:
        try:
            # --- MODIFICADO: enviamos final_message en lugar de message_text ---
            await callback.bot.send_message(u['telegram_id'], final_message)
            success += 1
        except Exception:
            failed += 1
            
    await state.clear()
    
    text = f"✅ <b>Broadcast Finished</b>\n\nSuccess: {success}\nFailed: {failed}"
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to Admin", callback_data="menu_admin")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)

@admin_router.callback_query(BroadcastState.confirm_broadcast, F.data == "bc_confirm_no")
async def cb_broadcast_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Broadcast cancelled.", reply_markup=get_broadcast_menu_keyboard())

@admin_router.callback_query(F.data == "admin_simulate_roles")
async def cb_simulate_roles(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    role = get_user_role(callback.from_user.id, user_data)
    
    if role not in ["admin", "dev"]:
        await callback.answer("Access Denied.", show_alert=True)
        return
        
    text = get_simulation_message("None Selected")
    keyboard = get_role_simulation_keyboard()
    await callback.message.edit_text(text, reply_markup=keyboard)

@admin_router.callback_query(F.data.startswith("sim_role_"))
async def cb_sim_role_view(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    actual_role = get_user_role(callback.from_user.id, user_data)
    
    if actual_role not in ["admin", "dev"]:
        await callback.answer("Access Denied.", show_alert=True)
        return
        
    simulated_role = callback.data.replace("sim_role_", "")
    has_checks = True if simulated_role in ["admin", "active_user", "expired_user", "dev"] else False
    
    text = get_simulation_message(simulated_role)
    keyboard = get_main_keyboard(simulated_role, has_checks)
    
    from aiogram.types import InlineKeyboardButton
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🛑 Stop Simulation", callback_data="menu_admin")])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@admin_router.callback_query(F.data.startswith("admin_devlogs_page_"))
async def cb_admin_devlogs(callback: CallbackQuery, db_pool):
    page = int(callback.data.split("_")[-1])
    limit = 5
    offset = (page - 1) * limit
    
    total_dates = await get_devlog_dates_count(db_pool)
    total_pages = math.ceil(total_dates / limit) if total_dates > 0 else 1
    
    dates = await get_devlog_dates_paginated(db_pool, limit, offset)
    
    text = get_devlog_dates_message(page, total_pages)
    if not dates:
        text += "\n<i>No devlogs found.</i>"
        
    keyboard = get_devlog_dates_keyboard(dates, page, total_pages)
    await callback.message.edit_text(text, reply_markup=keyboard)

@admin_router.callback_query(F.data.startswith("admin_devlog_view_"))
async def cb_admin_devlog_view(callback: CallbackQuery, db_pool):
    date_str = callback.data.split("admin_devlog_view_")[-1]
    log_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    logs = await get_devlogs_by_date(db_pool, log_date)
    
    text = get_devlog_content_message(date_str, logs)
    keyboard = get_devlog_message_keyboard()
    
    await callback.message.edit_text(text, reply_markup=keyboard)