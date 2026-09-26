def get_user_orders_menu_message(page: int, total_pages: int, total_orders: int) -> str:
    if total_orders == 0:
        return "<b>📦 Your Orders</b>\n\nYou have no order history yet."
    return f"<b>📦 Your Orders</b> (Page {page}/{total_pages})\n\nSelect an order below to view its details:"

def get_user_order_view_message(order_data: dict) -> str:
    status_map = {
        'pending': '🟧 Pending',
        'waiting': '🟧 Waiting',
        'confirming': '🟧 Confirming',
        'sending': '🟧 Sending',
        'completed': '🟩 Completed',
        'finished': '🟩 Completed',
        'failed': '🟥 Failed',
        'expired': '🟥 Expired',
        'timeout': '🟥 Cancelled by Timeout',
        'error': '🟥 Error'
    }
    status_text = status_map.get(order_data['payment_status'], f"🧾 {order_data['payment_status'].capitalize()}")
    date_str = order_data['created_at'].strftime("%Y-%m-%d %H:%M:%S")

    return (
        f"<b>🧾 Order Details</b>\n\n"
        f"<b>TXID:</b> <code>{order_data['transaction_id']}</code>\n"
        f"<b>Plan:</b> {order_data['plan_purchased'].capitalize()}\n"
        f"<b>Amount:</b> ${order_data['amount']}\n"
        f"<b>Status:</b> {status_text}\n"
        f"<b>Date:</b> {date_str}"
    )

def get_admin_orders_menu_message(stats: dict) -> str:
    comp_amt = stats['completed']['amount']
    pend_amt = stats['pending']['amount']
    
    return (
        "<b>🧾 Check Orders</b>\n\n"
        "<b>💰 Total Revenue Generated:</b>\n"
        f"• <b>Completed:</b> ${comp_amt:.2f}\n"
        f"• <b>Pending:</b> ${pend_amt:.2f}\n\n"
        "Select an order category to view global transactions:"
    )

def get_admin_orders_list_message(status: str, page: int, total_pages: int, total_orders: int) -> str:
    if total_orders == 0:
        return f"<b>🧾 {status.capitalize()} Orders</b>\n\nNo orders found in this category."
    return f"<b>🧾 {status.capitalize()} Orders</b> (Page {page}/{total_pages})\n\nSelect an order to view details:"

def get_admin_order_view_message(order_data: dict) -> str:
    date_str = order_data['created_at'].strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"<b>🧾 Global Order Details</b>\n\n"
        f"<b>User ID:</b> <code>{order_data['telegram_id']}</code>\n"
        f"<b>TXID:</b> <code>{order_data['transaction_id']}</code>\n"
        f"<b>Plan:</b> {order_data['plan_purchased'].capitalize()}\n"
        f"<b>Amount:</b> ${order_data['amount']}\n"
        f"<b>Status:</b> {order_data['payment_status'].capitalize()}\n"
        f"<b>Date:</b> {date_str}"
    )