import psutil
import platform
import time

BOT_START_TIME = time.time()
INITIAL_NET_IO = psutil.net_io_counters()

def get_dev_panel_message() -> str:
    return "<b>Developer Panel</b>\n\nSelect an option below to manage the bot:"

def get_maintenance_message(is_active: bool) -> str:
    status = "ACTIVE" if is_active else "OFF"
    return f"<b>Maintenance Mode</b>\n\nCurrent Status: <code>{status}</code>\n\nWhen active, regular users cannot interact with the bot."

def get_maintenance_confirm_message() -> str:
    return "<b>Are you sure you want to enable Maintenance Mode?</b>\n\nAll users will receive a broadcast message."

def get_system_metrics() -> dict:
    t0 = time.time()
    net_io_before = psutil.net_io_counters()
    
    cpu_percent = psutil.cpu_percent(interval=0.1)
    
    t1 = time.time()
    net_io_after = psutil.net_io_counters()
    
    time_diff = t1 - t0
    if time_diff == 0:
        time_diff = 0.1
        
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    total_sent = net_io_after.bytes_sent - INITIAL_NET_IO.bytes_sent
    total_recv = net_io_after.bytes_recv - INITIAL_NET_IO.bytes_recv
    
    speed_sent = (net_io_after.bytes_sent - net_io_before.bytes_sent) / time_diff
    speed_recv = (net_io_after.bytes_recv - net_io_before.bytes_recv) / time_diff
    
    return {
        "cpu": cpu_percent,
        "ram_used": memory.used / (1024 ** 3),
        "ram_total": memory.total / (1024 ** 3),
        "ram_percent": memory.percent,
        "disk_percent": disk.percent,
        "python_v": platform.python_version(),
        "net_total_sent": total_sent / (1024 ** 2),
        "net_total_recv": total_recv / (1024 ** 2),
        "net_speed_sent": speed_sent / 1024,
        "net_speed_recv": speed_recv / 1024
    }

def get_uptime_string() -> str:
    uptime_seconds = int(time.time() - BOT_START_TIME)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def get_bot_status_message(db_stats: dict, ping_ms: int, maintenance_active: bool) -> str:
    sys_metrics = get_system_metrics()
    uptime = get_uptime_string()
    
    maintenance_str = "ACTIVE" if maintenance_active else "OFF"
    
    return (
        "<b>Developer Diagnostics Panel</b>\n\n"
        
        "<b>Hardware & OS</b>\n"
        f"CPU Load: <code>{sys_metrics['cpu']}%</code>\n"
        f"RAM Usage: <code>{sys_metrics['ram_used']:.2f}GB / {sys_metrics['ram_total']:.2f}GB ({sys_metrics['ram_percent']}%)</code>\n"
        f"Disk Usage: <code>{sys_metrics['disk_percent']}%</code>\n"
        f"Environment: <code>Python {sys_metrics['python_v']}</code>\n\n"
        
        "<b>Network & Framework</b>\n"
        f"API Latency: <code>{ping_ms} ms</code>\n"
        f"Process Uptime: <code>{uptime}</code>\n"
        f"Current Bandwidth: <code>DL {sys_metrics['net_speed_recv']:.1f} KB/s | UL {sys_metrics['net_speed_sent']:.1f} KB/s</code>\n"
        f"Data Used (Uptime): <code>DL {sys_metrics['net_total_recv']:.1f} MB | UL {sys_metrics['net_total_sent']:.1f} MB</code>\n"
        f"Framework: <code>Aiogram 3.x</code>\n\n"
        
        "<b>Database Statistics</b>\n"
        f"Active Connections: <code>{db_stats['active_connections']}</code>\n"
        f"Database Size: <code>{db_stats['db_size']}</code>\n"
        f"Total Users: <code>{db_stats['total_users']}</code>\n"
        f"Total Payments: <code>{db_stats['total_payments']}</code>\n\n"
        
        "<b>Operations</b>\n"
        f"Maintenance Mode: <code>{maintenance_str}</code>\n"
        f"Pending Tickets: <code>{db_stats['pending_tickets']}</code>"
    )