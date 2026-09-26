import math
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.repo_users import get_user
from database.repo_orders import mark_orders_viewed, get_user_orders_paginated, get_user_orders_count, get_admin_orders_count, get_admin_orders_paginated, get_order, get_admin_order_stats
from utils.roles import get_user_role
from utils.keyboards.orders import get_user_orders_keyboard, get_user_order_view_keyboard, get_admin_orders_menu_keyboard, get_admin_orders_list_keyboard, get_admin_order_view_keyboard
from utils.messages.orders import get_user_orders_menu_message, get_user_order_view_message, get_admin_orders_menu_message, get_admin_orders_list_message, get_admin_order_view_message

orders_router = Router()

@orders_router.callback_query(F.data == "menu_orders")
async def cb_user_orders_first_page(callback: CallbackQuery, db_pool, state: FSMContext):
    await mark_orders_viewed(db_pool, callback.from_user.id)
    await cb_user_orders_page(callback, db_pool, state, 1)

@orders_router.callback_query(F.data.startswith("user_orders_page_"))
async def cb_user_orders_page_nav(callback: CallbackQuery, db_pool, state: FSMContext):
    page = int(callback.data.split("_")[-1])
    await cb_user_orders_page(callback, db_pool, state, page)

async def cb_user_orders_page(callback: CallbackQuery, db_pool, state: FSMContext, page: int):
    await state.update_data(orders_page=page)
    limit = 5
    offset = (page - 1) * limit
    
    total_orders = await get_user_orders_count(db_pool, callback.from_user.id)
    total_pages = math.ceil(total_orders / limit) if total_orders > 0 else 1
    
    orders = await get_user_orders_paginated(db_pool, callback.from_user.id, limit, offset)
    
    text = get_user_orders_menu_message(page, total_pages, total_orders)
    keyboard = get_user_orders_keyboard(orders, page, total_pages)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@orders_router.callback_query(F.data.startswith("user_order_view_"))
async def cb_user_order_view(callback: CallbackQuery, db_pool, state: FSMContext):
    txid = callback.data.replace("user_order_view_", "")
    order_record = await get_order(db_pool, txid)
    
    if not order_record:
        await callback.answer("Order not found.", show_alert=True)
        return
        
    order = dict(order_record)
    
    if order['payment_status'] in ['pending', 'waiting']:
        if datetime.now() - order['created_at'] > timedelta(minutes=30):
            async with db_pool.acquire() as conn:
                await conn.execute("UPDATE payments SET payment_status = 'timeout' WHERE transaction_id = $1", txid)
            order['payment_status'] = 'timeout'
            
    data = await state.get_data()
    page = data.get("orders_page", 1)
    
    text = get_user_order_view_message(order)
    keyboard = get_user_order_view_keyboard(page, order['payment_status'], order['plan_purchased'])
    await callback.message.edit_text(text, reply_markup=keyboard)

@orders_router.callback_query(F.data == "admin_check_orders")
async def cb_admin_check_orders_menu(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    role = get_user_role(callback.from_user.id, user_data)
    
    if role not in ["admin", "dev"]:
        return
        
    stats = await get_admin_order_stats(db_pool)
        
    text = get_admin_orders_menu_message(stats)
    keyboard = get_admin_orders_menu_keyboard(stats)
    await callback.message.edit_text(text, reply_markup=keyboard)

@orders_router.callback_query(F.data.startswith("admin_orders_"))
async def cb_admin_orders_list(callback: CallbackQuery, db_pool, state: FSMContext):
    user_data = await get_user(db_pool, callback.from_user.id)
    role = get_user_role(callback.from_user.id, user_data)
    
    if role not in ["admin", "dev"]:
        return
        
    if "_page_" not in callback.data:
        return
        
    parts = callback.data.split("_")
    status = parts[2]
    page = int(parts[-1])
    
    await state.update_data(admin_orders_status=status, admin_orders_page=page)
    
    limit = 5
    offset = (page - 1) * limit
    
    total_orders = await get_admin_orders_count(db_pool, status)
    total_pages = math.ceil(total_orders / limit) if total_orders > 0 else 1
    
    orders = await get_admin_orders_paginated(db_pool, status, limit, offset)
    
    text = get_admin_orders_list_message(status, page, total_pages, total_orders)
    keyboard = get_admin_orders_list_keyboard(status, orders, page, total_pages)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@orders_router.callback_query(F.data.startswith("admin_order_view_"))
async def cb_admin_order_view(callback: CallbackQuery, db_pool, state: FSMContext):
    user_data = await get_user(db_pool, callback.from_user.id)
    role = get_user_role(callback.from_user.id, user_data)
    
    if role not in ["admin", "dev"]:
        return
        
    txid = callback.data.replace("admin_order_view_", "")
    order = await get_order(db_pool, txid)
    
    if not order:
        await callback.answer("Order not found.", show_alert=True)
        return
        
    data = await state.get_data()
    page = data.get("admin_orders_page", 1)
    status = data.get("admin_orders_status", "completed")
    
    text = get_admin_order_view_message(order)
    keyboard = get_admin_order_view_keyboard(status, page)
    await callback.message.edit_text(text, reply_markup=keyboard)