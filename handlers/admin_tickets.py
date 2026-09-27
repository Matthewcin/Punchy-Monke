import math
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot
from database.repo_users import get_user
from database.repo_tickets import get_admin_tickets_count, get_admin_tickets_paginated, get_ticket, update_ticket_status, delete_ticket, update_admin_reply, get_admin_ticket_stats
from utils.roles import get_user_role
from utils.keyboards.tickets import get_admin_tickets_main_keyboard, get_admin_tickets_list_keyboard, get_admin_ticket_action_keyboard, get_admin_discard_confirm_keyboard, get_admin_reply_confirm_keyboard, get_cancel_keyboard
from utils.messages.tickets import get_admin_ticket_menu_message, get_admin_ticket_list_message, get_admin_ticket_view_message, get_admin_reply_prompt_message, get_ticket_confirm_message, get_user_ticket_notification

admin_tickets_router = Router()

class AdminTicketState(StatesGroup):
    waiting_for_admin_reply = State()
    waiting_for_reply_confirmation = State()

@admin_tickets_router.callback_query(F.data == "admin_check_tickets")
async def cb_admin_check_tickets(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    role = get_user_role(callback.from_user.id, user_data)
    
    if role not in ["admin", "dev"]:
        return
        
    stats = await get_admin_ticket_stats(db_pool)
    await callback.message.edit_text(get_admin_ticket_menu_message(), reply_markup=get_admin_tickets_main_keyboard(stats))

@admin_tickets_router.callback_query(F.data.startswith("admin_ticket_cat_"))
async def cb_admin_ticket_category(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    if get_user_role(callback.from_user.id, user_data) not in ["admin", "dev"]:
        return
        
    parts = callback.data.split("_")
    ticket_type = parts[3]
    page = int(parts[-1])
    
    limit = 5
    offset = (page - 1) * limit
    
    count = await get_admin_tickets_count(db_pool, ticket_type)
    total_pages = math.ceil(count / limit) if count > 0 else 1
    
    tickets = await get_admin_tickets_paginated(db_pool, ticket_type, limit, offset)
    
    text = get_admin_ticket_list_message(ticket_type, page, total_pages, count)
    keyboard = get_admin_tickets_list_keyboard(ticket_type, tickets, page, total_pages)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@admin_tickets_router.callback_query(F.data.startswith("admin_ticket_view_"))
async def cb_admin_ticket_view(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    if get_user_role(callback.from_user.id, user_data) not in ["admin", "dev"]:
        return
        
    ticket_id = int(callback.data.replace("admin_ticket_view_", ""))
    ticket = await get_ticket(db_pool, ticket_id)
    
    if not ticket:
        return await callback.answer("Ticket not found.", show_alert=True)
        
    text = get_admin_ticket_view_message(dict(ticket))
    keyboard = get_admin_ticket_action_keyboard(ticket_id)
    
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        pass

@admin_tickets_router.callback_query(F.data.startswith("admin_ticket_read_"))
async def cb_admin_ticket_read(callback: CallbackQuery, db_pool):
    ticket_id = int(callback.data.replace("admin_ticket_read_", ""))
    await update_ticket_status(db_pool, ticket_id, 'readed')
    await callback.answer("Marked as read.", show_alert=True)
    callback.data = f"admin_ticket_view_{ticket_id}"
    await cb_admin_ticket_view(callback, db_pool)

@admin_tickets_router.callback_query(F.data.startswith("admin_ticket_discard_"))
async def cb_admin_ticket_discard(callback: CallbackQuery):
    ticket_id = int(callback.data.replace("admin_ticket_discard_", ""))
    text = "<b>⚠️ Are you sure that you want to delete this ticket?</b>"
    keyboard = get_admin_discard_confirm_keyboard(ticket_id)
    await callback.message.edit_text(text, reply_markup=keyboard)

@admin_tickets_router.callback_query(F.data.startswith("admin_ticket_del_yes_"))
async def cb_admin_ticket_del_yes(callback: CallbackQuery, db_pool):
    ticket_id = int(callback.data.replace("admin_ticket_del_yes_", ""))
    await delete_ticket(db_pool, ticket_id)
    await callback.answer("Ticket deleted successfully.", show_alert=True)
    await cb_admin_check_tickets(callback, db_pool)

@admin_tickets_router.callback_query(F.data.startswith("admin_ticket_del_no_"))
async def cb_admin_ticket_del_no(callback: CallbackQuery, db_pool):
    ticket_id = int(callback.data.replace("admin_ticket_del_no_", ""))
    callback.data = f"admin_ticket_view_{ticket_id}"
    await cb_admin_ticket_view(callback, db_pool)

@admin_tickets_router.callback_query(F.data.startswith("admin_ticket_reply_"))
async def cb_admin_ticket_reply(callback: CallbackQuery, state: FSMContext):
    ticket_id = int(callback.data.replace("admin_ticket_reply_", ""))
    await state.update_data(reply_ticket_id=ticket_id)
    await state.set_state(AdminTicketState.waiting_for_admin_reply)
    await callback.message.edit_text(get_admin_reply_prompt_message(), reply_markup=get_cancel_keyboard())

@admin_tickets_router.message(AdminTicketState.waiting_for_admin_reply)
async def process_admin_reply(message: Message, state: FSMContext):
    await state.update_data(admin_message=message.text)
    await state.set_state(AdminTicketState.waiting_for_reply_confirmation)
    await message.answer(get_ticket_confirm_message(message.text), reply_markup=get_admin_reply_confirm_keyboard())

@admin_tickets_router.callback_query(F.data == "admin_ticket_rep_yes")
async def cb_admin_ticket_rep_yes(callback: CallbackQuery, state: FSMContext, db_pool, bot: Bot):
    data = await state.get_data()
    ticket_id = data.get("reply_ticket_id")
    admin_message = data.get("admin_message")
    
    ticket = await get_ticket(db_pool, ticket_id)
    if ticket:
        await update_admin_reply(db_pool, ticket_id, admin_message)
        try:
            notification = get_user_ticket_notification(admin_message)
            await bot.send_message(ticket['telegram_id'], notification)
        except Exception:
            pass
            
    await state.clear()
    await callback.message.edit_text("<b>✅ Response sent to the user successfully.</b>", reply_markup=get_cancel_keyboard())

@admin_tickets_router.callback_query(F.data == "admin_ticket_rep_no")
async def cb_admin_ticket_rep_no(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminTicketState.waiting_for_admin_reply)
    await callback.message.edit_text("<b>✍️ Please re-enter your message:</b>", reply_markup=get_cancel_keyboard())