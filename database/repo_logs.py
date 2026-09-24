async def get_user_checks_count(pool, telegram_id):
    async with pool.acquire() as conn:
        count = await conn.fetchval('''
            SELECT COUNT(*) FROM check_logs WHERE telegram_id = $1
        ''', telegram_id)
        return count if count else 0

async def get_user_checks_paginated(pool, telegram_id, limit, offset):
    async with pool.acquire() as conn:
        return await conn.fetch('''
            SELECT provider, result_status, check_timestamp 
            FROM check_logs 
            WHERE telegram_id = $1 
            ORDER BY check_timestamp DESC 
            LIMIT $2 OFFSET $3
        ''', telegram_id, limit, offset)