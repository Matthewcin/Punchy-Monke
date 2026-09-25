async def get_setting(pool, key: str) -> str:
    async with pool.acquire() as conn:
        val = await conn.fetchval('SELECT setting_value FROM bot_settings WHERE setting_key = $1', key)
        return val or "false"

async def set_setting(pool, key: str, value: str):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO bot_settings (setting_key, setting_value)
            VALUES ($1, $2)
            ON CONFLICT (setting_key) DO UPDATE SET setting_value = $2
        ''', key, value)