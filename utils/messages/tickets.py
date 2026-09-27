def get_support_menu_message() -> str:
    return "<b>🎫 Support Center</b>\n\nHow can we help you today?"

def get_support_categories_message() -> str:
    return "<b>🎫 Support Center</b>\n\nPlease select the category for your new ticket:"

def get_active_ticket_message() -> str:
    return "<b>🎫 Support Center</b>\n\nYou currently have an active ticket open. Please wait for the staff to reply or manage it below."

def get_ticket_prompt_message(ticket_type: str) -> str:
    return f"<b>📝 Creating a {ticket_type.capitalize()} Ticket</b>\n\nPlease send the detailed message you want to submit to our support team:"

def get_ticket_confirm_message(message_text: str) -> str:
    return f"<b>⚠️ Are you sure you want to send this message?</b>\n\n<b>Your Message:</b>\n{message_text}"

def get_ticket_created_message() -> str:
    return "<b>✅ Ticket Created</b>\n\nYour ticket has been submitted successfully. Our staff will review it shortly."

def get_admin_ticket_menu_message() -> str:
    return "<b>🛠 Support Tickets Management</b>\n\nSelect a category to fetch tickets from oldest to newest:"

def get_admin_ticket_list_message(ticket_type: str, page: int, total_pages: int, count: int) -> str:
    if count == 0:
        return f"<b>📂 {ticket_type.capitalize()} Tickets</b>\n\nNo pending tickets found in this category."
    return f"<b>📂 {ticket_type.capitalize()} Tickets</b> (Page {page}/{total_pages})\n\nSelect a ticket to manage:"

def get_admin_ticket_view_message(ticket: dict) -> str:
    date_str = ticket['created_at'].strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"<b>🎟 Ticket ID:</b> <code>{ticket['ticket_id']}</code>\n"
        f"<b>👤 User ID:</b> <code>{ticket['telegram_id']}</code>\n"
        f"<b>📂 Type:</b> {ticket['ticket_type'].capitalize()}\n"
        f"<b>📌 Status:</b> {ticket['status'].capitalize()}\n"
        f"<b>📅 Created:</b> {date_str}\n\n"
        f"<b>💬 User Message:</b>\n{ticket['user_message']}"
    )

def get_admin_reply_prompt_message() -> str:
    return "<b>✍️ Reply to Ticket</b>\n\nPlease send the message you want to send as a reply to this user:"

def get_user_ticket_notification(admin_message: str) -> str:
    return f"<b>🔔 Ticket Update</b>\n\nHello! Your ticket has been checked by the Staff...\n\n<code>{admin_message}</code>"

def get_user_ticket_view_message(ticket: dict) -> str:
    date_str = ticket['updated_at'].strftime("%Y-%m-%d %H:%M:%S")
    text = (
        f"<b>🎟 Ticket ID:</b> <code>{ticket['ticket_id']}</code>\n"
        f"<b>📂 Type:</b> {ticket['ticket_type'].capitalize()}\n"
        f"<b>📌 Status:</b> {ticket['status'].capitalize()}\n"
        f"<b>📅 Last Update:</b> {date_str}\n\n"
        f"<b>💬 Your Message:</b>\n{ticket['user_message']}"
    )
    if ticket['admin_message']:
        text += f"\n\n<b>👨‍💻 Admin Reply:</b>\n<code>{ticket['admin_message']}</code>"
    return text