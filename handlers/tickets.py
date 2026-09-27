import math
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.repo_tickets import create_ticket, get_user_tickets_count, get_user_tickets_paginated, get_ticket, update_ticket_status, update_user_reply, get_user_active_ticket
from utils.keyboards.tickets import get_support_main_keyboard, get_support_categories_keyboard, get_support_active_keyboard, get_cancel_keyboard, get_ticket_confirm_keyboard, get_user_tickets_list_keyboard, get_user_ticket_action_keyboard
from utils.messages.tickets import get_support_menu_message, get_support_categories_message, get_active_ticket_message, get_ticket_prompt_message, get_ticket_confirm_message, get_ticket_created_message, get_user_ticket_view_message

tickets_router = Router()

class TicketState(StatesGroup):
    waiting_for_message = State()
    waiting_for_confirmation = State()
    waiting_for_user_reply = State()
    waiting_for_reply_confirmation = State()

@tickets_router.callback_query(F.data == "menu_support")
async def cb_support_menu(callback: CallbackQuery, state: FSMContext, db_pool):
    await state.clear()
    active_ticket = await get_user_active_ticket(db_pool, callback.from_user.id)
    
    if active_ticket:
        await callback.message.edit_text(get_active_ticket_message(), reply_markup=get_support_active_keyboard(active_ticket['ticket_id']))
    else:
        await callback.message.edit_text(get_support_menu_message(), reply_markup=get_support_main_keyboard())

@tickets_router.callback_query(F.data == "ticket_create_menu")
async def cb_ticket_create_menu(callback: CallbackQuery, db_pool):
    active_ticket = await get_user_active_ticket(db_pool, callback.from_user.id)
    if active_ticket:
        await callback.answer("You already have an active ticket open.", show_alert=True)
        return
    await callback.message.edit_text(get_support_categories_message(), reply_markup=get_support_categories_keyboard())

@tickets_router.callback_query(F.data.in_({"ticket_new_payment", "ticket_new_bug", "ticket_new_error", "ticket_new_help"}))
async def cb_create_ticket(callback: CallbackQuery, state: FSMContext):
    ticket_type = callback.data.replace("ticket_new_", "")
    await state.update_data(ticket_type=ticket_type)
    await state.set_state(TicketState.waiting_for_message)
    await callback.message.edit_text(get_ticket_prompt_message(ticket_type), reply_markup=get_cancel_keyboard())

@tickets_router.message(TicketState.waiting_for_message)
async def process_ticket_message(message: Message, state: FSMContext):
    await state.update_data(user_message=message.text)
    await state.set_state(TicketState.waiting_for_confirmation)
    await message.answer(get_ticket_confirm_message(message.text), reply_markup=get_ticket_confirm_keyboard())

@tickets_router.callback_query(F.data == "ticket_confirm_yes")
async def cb_ticket_confirm_yes(callback: CallbackQuery, state: FSMContext, db_pool):
    data = await state.get_data()
    ticket_type = data.get("ticket_type")
    user_message = data.get("user_message")
    ticket_id_reply = data.get("reply_ticket_id")
    
    if ticket_id_reply:
        await update_user_reply(db_pool, int(ticket_id_reply), user_message)
    elif ticket_type and user_message:
        await create_ticket(db_pool, callback.from_user.id, ticket_type, user_message)
        
    await state.clear()
    await callback.message.edit_text(get_ticket_created_message(), reply_markup=get_cancel_keyboard())

@tickets_router.callback_query(F.data == "ticket_confirm_no")
async def cb_ticket_confirm_no(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get("reply_ticket_id"):
        await state.set_state(TicketState.waiting_for_user_reply)
        await callback.message.edit_text("Please send your new message:", reply_markup=get_cancel_keyboard())
    else:
        ticket_type = data.get("ticket_type")
        await state.set_state(TicketState.waiting_for_message)
        await callback.message.edit_text(get_ticket_prompt_message(ticket_type), reply_markup=get_cancel_keyboard())

@tickets_router.callback_query(F.data.startswith("ticket_user_list_"))
async def cb_user_tickets_list(callback: CallbackQuery, db_pool):
    page = int(callback.data.split("_")[-1])
    limit = 5
    offset = (page - 1) * limit
    
    total_tickets = await get_user_tickets_count(db_pool, callback.from_user.id)
    total_pages = math.ceil(total_tickets / limit) if total_tickets > 0 else 1
    
    tickets = await get_user_tickets_paginated(db_pool, callback.from_user.id, limit, offset)
    
    text = f"<b>📚 Ticket History</b> (Page {page}/{total_pages})\n\nSelect a ticket to view details:"
    if total_tickets == 0:
        text = "<b>📚 Ticket History</b>\n\nYou have no support tickets."
        
    keyboard = get_user_tickets_list_keyboard(tickets, page, total_pages)
    await callback.message.edit_text(text, reply_markup=keyboard)

@tickets_router.callback_query(F.data.startswith("ticket_user_view_"))
async def cb_user_ticket_view(callback: CallbackQuery, db_pool):
    ticket_id = int(callback.data.replace("ticket_user_view_", ""))
    ticket = await get_ticket(db_pool, ticket_id)
    
    if not ticket:
        return await callback.answer("Ticket not found.", show_alert=True)
        
    text = get_user_ticket_view_message(dict(ticket))
    keyboard = get_user_ticket_action_keyboard(ticket_id, ticket['status'])
    
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        pass

@tickets_router.callback_query(F.data.startswith("ticket_user_solve_"))
async def cb_user_ticket_solve(callback: CallbackQuery, db_pool):
    ticket_id = int(callback.data.replace("ticket_user_solve_", ""))
    await update_ticket_status(db_pool, ticket_id, 'solved')
    await callback.answer("Ticket marked as solved.", show_alert=True)
    callback.data = f"ticket_user_view_{ticket_id}"
    await cb_user_ticket_view(callback, db_pool)

@tickets_router.callback_query(F.data.startswith("ticket_user_reply_"))
async def cb_user_ticket_reply(callback: CallbackQuery, state: FSMContext):
    ticket_id = int(callback.data.replace("ticket_user_reply_", ""))
    await state.update_data(reply_ticket_id=ticket_id)
    await state.set_state(TicketState.waiting_for_user_reply)
    await callback.message.edit_text("<b>✍️ Reply to Admin</b>\n\nPlease send your response:", reply_markup=get_cancel_keyboard())

@tickets_router.message(TicketState.waiting_for_user_reply)
async def process_ticket_user_reply(message: Message, state: FSMContext):
    await state.update_data(user_message=message.text)
    await state.set_state(TicketState.waiting_for_reply_confirmation)
    await message.answer(get_ticket_confirm_message(message.text), reply_markup=get_ticket_confirm_keyboard())