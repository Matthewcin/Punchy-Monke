def get_dev_panel_message() -> str:
    text = (
        "<b>👨‍💻 Developer Panel</b>\n\n"
        "Welcome to the core management system. Select a tool below."
    )
    return text

def get_simulation_message(role: str) -> str:
    text = (
        "<b>🎭 Role Simulation</b>\n\n"
        f"Select a role to preview how the Main Menu looks for them.\n"
        f"Currently previewing: <b>{role.replace('_', ' ').capitalize()}</b>\n\n"
        "<i>Note: Buttons will execute normally based on your actual database permissions.</i>"
    )
    return text