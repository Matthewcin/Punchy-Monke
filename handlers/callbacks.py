import math
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.repo_users import get_user
from database.repo_logs import get_user_checks_count, get_user_checks_paginated
from utils.roles import get_user_role
from utils.keyboards import get_main_keyboard, get_pagination_keyboard
from utils.messages.start import get_start_message

callback_router = Router()

@callback_router.callback_query(F.data == "go_back")
async def cb_go_back(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    checks_count = await get_user_checks_count(db_pool, callback.from_user.id)
    
    has_checks = checks_count > 0
    role = get_user_role(callback.from_user.id, user_data)
    
    keyboard = get_main_keyboard(role, has_checks)
    text = get_start_message(callback.from_user.first_name, callback.from_user.id, user_data)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@callback_router.callback_query(F.data == "menu_latest_checks")
async def cb_latest_checks(callback: CallbackQuery, db_pool):
    await send_checks_page(callback, db_pool, page=1)

@callback_router.callback_query(F.data.startswith("checks_page_"))
async def cb_checks_pagination(callback: CallbackQuery, db_pool):
    page = int(callback.data.split("_")[-1])
    await send_checks_page(callback, db_pool, page=page)

async def send_checks_page(callback: CallbackQuery, db_pool, page: int):
    limit = 5
    offset = (page - 1) * limit
    telegram_id = callback.from_user.id
    
    total_checks = await get_user_checks_count(db_pool, telegram_id)
    total_pages = math.ceil(total_checks / limit)
    
    checks = await get_user_checks_paginated(db_pool, telegram_id, limit, offset)
    
    text = f"<b>📋 Latest Checks</b> (Page {page}/{total_pages})\n\n"
    
    if not checks:
        text += "<i>No history found.</i>"
    else:
        for check in checks:
            date_str = check['check_timestamp'].strftime("%Y-%m-%d %H:%M")
            text += f"• <b>{check['provider']}</b> - {check['result_status']} (<code>{date_str}</code>)\n"
            
    keyboard = get_pagination_keyboard(page, total_pages)
    await callback.message.edit_text(text, reply_markup=keyboard)