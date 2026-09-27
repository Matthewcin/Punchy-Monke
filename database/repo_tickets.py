async def create_ticket(pool, telegram_id: int, ticket_type: str, user_message: str):
    async with pool.acquire() as conn:
        return await conn.fetchval('''
            INSERT INTO support_tickets (telegram_id, ticket_type, user_message)
            VALUES ($1, $2, $3) RETURNING ticket_id
        ''', telegram_id, ticket_type, user_message)

async def get_ticket(pool, ticket_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow('SELECT * FROM support_tickets WHERE ticket_id = $1', ticket_id)

async def get_user_active_ticket(pool, telegram_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow('''
            SELECT * FROM support_tickets 
            WHERE telegram_id = $1 AND status != 'solved'
            LIMIT 1
        ''', telegram_id)

async def update_ticket_status(pool, ticket_id: int, status: str):
    async with pool.acquire() as conn:
        await conn.execute('''
            UPDATE support_tickets 
            SET status = $1, updated_at = CURRENT_TIMESTAMP 
            WHERE ticket_id = $2
        ''', status, ticket_id)

async def update_admin_reply(pool, ticket_id: int, admin_message: str):
    async with pool.acquire() as conn:
        await conn.execute('''
            UPDATE support_tickets 
            SET admin_message = $1, status = 'replied', updated_at = CURRENT_TIMESTAMP 
            WHERE ticket_id = $2
        ''', admin_message, ticket_id)

async def update_user_reply(pool, ticket_id: int, user_message: str):
    async with pool.acquire() as conn:
        await conn.execute('''
            UPDATE support_tickets 
            SET user_message = $1, status = 'unsolved', updated_at = CURRENT_TIMESTAMP 
            WHERE ticket_id = $2
        ''', user_message, ticket_id)

async def delete_ticket(pool, ticket_id: int):
    async with pool.acquire() as conn:
        await conn.execute('DELETE FROM support_tickets WHERE ticket_id = $1', ticket_id)

async def get_user_tickets_paginated(pool, telegram_id: int, limit: int, offset: int):
    async with pool.acquire() as conn:
        return await conn.fetch('''
            SELECT * FROM support_tickets 
            WHERE telegram_id = $1 
            ORDER BY updated_at DESC 
            LIMIT $2 OFFSET $3
        ''', telegram_id, limit, offset)

async def get_user_tickets_count(pool, telegram_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchval('SELECT COUNT(*) FROM support_tickets WHERE telegram_id = $1', telegram_id)

async def get_admin_tickets_paginated(pool, ticket_type: str, limit: int, offset: int):
    async with pool.acquire() as conn:
        return await conn.fetch('''
            SELECT * FROM support_tickets 
            WHERE ticket_type = $1 AND status != 'solved'
            ORDER BY created_at ASC 
            LIMIT $2 OFFSET $3
        ''', ticket_type, limit, offset)

async def get_admin_tickets_count(pool, ticket_type: str):
    async with pool.acquire() as conn:
        return await conn.fetchval('''
            SELECT COUNT(*) FROM support_tickets 
            WHERE ticket_type = $1 AND status != 'solved'
        ''', ticket_type)

async def get_admin_ticket_stats(pool):
    async with pool.acquire() as conn:
        records = await conn.fetch('''
            SELECT ticket_type, COUNT(*) as count
            FROM support_tickets 
            WHERE status != 'solved'
            GROUP BY ticket_type
        ''')
        stats = {'payment': 0, 'bug': 0, 'error': 0, 'help': 0}
        for r in records:
            stats[r['ticket_type']] = r['count']
        return stats