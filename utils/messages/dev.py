def get_dev_panel_message() -> str:
    text = (
        "<b>👨‍💻 Developer Panel</b>\n\n"
        "Welcome to the core management system. Select a tool below."
    )
    return text

def get_maintenance_message(is_active: bool) -> str:
    status = "🟢 Active" if is_active else "🔴 Inactive"
    text = (
        "<b>🚧 Maintenance Mode</b>\n\n"
        f"Current Status: <b>{status}</b>\n\n"
        "Toggle the maintenance mode below. When turned ON, a broadcast will be sent to all users and non-admins will be blocked."
    )
    return text

def get_maintenance_confirm_message() -> str:
    text = (
        "⚠️ <b>ARE YOU SURE THAT YOU WANT TO SET MAINTENANCE MODE?</b>\n\n"
        "This will instantly broadcast a maintenance message to all users and block their access."
    )
    return text