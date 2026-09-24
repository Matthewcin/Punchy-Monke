def get_admin_panel_message() -> str:
    text = (
        "<b>⚙️ Admin Panel</b>\n\n"
        "Welcome to the management system. Select an option below to view logs or manage the bot."
    )
    return text

def get_devlog_dates_message(page: int, total_pages: int) -> str:
    text = (
        f"<b>🐛 Developer Logs</b> (Page {page}/{total_pages})\n\n"
        "Select a date to read the technical updates and patches."
    )
    return text

def get_devlog_content_message(date_str: str, logs: list) -> str:
    text = f"<b>📅 DevLog for {date_str}</b>\n\n"
    
    for idx, log in enumerate(logs, 1):
        time_str = log['created_at'].strftime("%H:%M:%S")
        text += f"<code>[{time_str}]</code>\n{log['message']}\n\n"
        
    return text