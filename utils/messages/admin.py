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

def get_simulation_message(role: str) -> str:
    text = (
        "<b>🎭 Role Simulation</b>\n\n"
        f"Select a role to preview how the Main Menu looks for them.\n"
        f"Currently previewing: <b>{role.replace('_', ' ').capitalize()}</b>\n\n"
        "<i>Note: Buttons will execute normally based on your actual database permissions.</i>"
    )
    return text

def get_broadcast_prompt_message(target_type: str, counter: int) -> str:
    prompts = {
        "all": f"Please type the message for ALL USERS ({counter})",
        "expired": f"Please type the message for Expired Users Only ({counter})",
        "active": f"Please type the message for Users with Active Plan Only ({counter})",
        "new": f"Please type the message for New Members ({counter})",
        "trial": f"Please type the message for Trial Members ({counter})"
    }
    return prompts.get(target_type, "Please type the message:")

def get_broadcast_confirm_message(target_type: str, counter: int) -> str:
    confirms = {
        "all": f"Are you sure that you want to send This Message to {counter} Users?",
        "expired": f"Are you sure that you want to send This Message to {counter} Expired Users?",
        "active": f"Are you sure that you want to send This Message to {counter} Active Users?",
        "new": f"Are you sure that you want to send This Message to {counter} New Users?",
        "trial": f"Are you sure that you want to send This Message to {counter} Trial Users?"
    }
    return confirms.get(target_type, "Are you sure?")