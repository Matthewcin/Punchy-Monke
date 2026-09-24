import math
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.repo_users import get_user
from database.repo_devlogs import get_devlog_dates_count, get_devlog_dates_paginated, get_devlogs_by_date
from utils.roles import get_user_role
from utils.keyboards import get_admin_panel_keyboard, get_devlog_dates_keyboard, get_devlog_message_keyboard
from utils.messages.admin import get_admin_panel_message, get_devlog_dates_message, get_devlog_content_message

admin_router = Router()

@admin_router.callback_query(F.data == "menu_admin")
async def cb_admin_panel(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    role = get_user_role(callback.from_user.id, user_data)
    
    if role not in ["admin", "dev"]:
        await callback.answer("Access Denied.", show_alert=True)
        return
        
    text = get_admin_panel_message()
    keyboard = get_admin_panel_keyboard(role)
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