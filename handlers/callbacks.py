from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.repo_users import get_user
from database.repo_logs import get_user_batches_count
from database.repo_orders import get_user_order_status, get_user_orders_count
from utils.roles import get_user_role
from utils.keyboards.user import get_main_keyboard
from utils.messages.start import get_start_message

callback_router = Router()

@callback_router.callback_query(F.data == "go_back")
async def cb_go_back(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    checks_count = await get_user_batches_count(db_pool, callback.from_user.id)
    orders_count = await get_user_orders_count(db_pool, callback.from_user.id)
    
    has_checks = checks_count > 0
    has_orders = orders_count > 0
    has_used_trial = user_data.get('has_used_trial', False) if user_data else False
    role = get_user_role(callback.from_user.id, user_data)
    orders_emoji = await get_user_order_status(db_pool, callback.from_user.id)
    
    keyboard = get_main_keyboard(role, has_checks, orders_emoji, has_orders, has_used_trial)
    text = get_start_message(callback.from_user.first_name, callback.from_user.id, user_data)
    
    await callback.message.edit_text(text, reply_markup=keyboard)