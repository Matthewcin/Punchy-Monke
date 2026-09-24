async def add_devlog(pool, message_text: str):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO devlogs (message) VALUES ($1)
        ''', message_text)

async def get_devlog_dates_count(pool):
    async with pool.acquire() as conn:
        count = await conn.fetchval('SELECT COUNT(DISTINCT log_date) FROM devlogs')
        return count if count else 0

async def get_devlog_dates_paginated(pool, limit: int, offset: int):
    async with pool.acquire() as conn:
        return await conn.fetch('''
            SELECT DISTINCT log_date FROM devlogs
            ORDER BY log_date DESC
            LIMIT $1 OFFSET $2
        ''', limit, offset)

async def get_devlogs_by_date(pool, log_date):
    async with pool.acquire() as conn:
        return await conn.fetch('''
            SELECT message, created_at FROM devlogs
            WHERE log_date = $1
            ORDER BY created_at ASC
        ''', log_date)