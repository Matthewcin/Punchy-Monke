async def get_user_order_status(pool, telegram_id: int):
    async with pool.acquire() as conn:
        records = await conn.fetch('SELECT payment_status, viewed FROM payments WHERE telegram_id = $1', telegram_id)
        if not records:
            return "📦"
        
        has_pending = any(r['payment_status'] in ['pending', 'waiting', 'confirming', 'sending'] for r in records)
        if has_pending:
            return "🟧"
            
        has_success = any(r['payment_status'] in ['completed', 'finished'] and not r['viewed'] for r in records)
        if has_success:
            return "🟩"
            
        has_fail = any(r['payment_status'] in ['failed', 'expired', 'error', 'timeout'] and not r['viewed'] for r in records)
        if has_fail:
            return "🟥"
            
        return "🧾"

async def mark_orders_viewed(pool, telegram_id: int):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE payments SET viewed = TRUE WHERE telegram_id = $1 AND payment_status NOT IN ('pending', 'waiting', 'confirming', 'sending')", telegram_id)

async def get_user_orders_paginated(pool, telegram_id: int, limit: int, offset: int):
    async with pool.acquire() as conn:
        return await conn.fetch('''
            SELECT transaction_id, amount, plan_purchased, payment_status, created_at 
            FROM payments 
            WHERE telegram_id = $1 
            ORDER BY created_at DESC 
            LIMIT $2 OFFSET $3
        ''', telegram_id, limit, offset)

async def get_user_orders_count(pool, telegram_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchval('SELECT COUNT(*) FROM payments WHERE telegram_id = $1', telegram_id)

async def get_admin_orders_paginated(pool, status_filter: str, limit: int, offset: int):
    async with pool.acquire() as conn:
        if status_filter == "pending":
            where = "payment_status IN ('pending', 'waiting', 'confirming', 'sending')"
        elif status_filter == "completed":
            where = "payment_status IN ('completed', 'finished')"
        else:
            where = "payment_status IN ('failed', 'expired', 'error', 'timeout')"
            
        return await conn.fetch(f'''
            SELECT transaction_id, telegram_id, amount, plan_purchased, payment_status, created_at 
            FROM payments 
            WHERE {where}
            ORDER BY created_at DESC 
            LIMIT $1 OFFSET $2
        ''', limit, offset)

async def get_admin_orders_count(pool, status_filter: str):
    async with pool.acquire() as conn:
        if status_filter == "pending":
            where = "payment_status IN ('pending', 'waiting', 'confirming', 'sending')"
        elif status_filter == "completed":
            where = "payment_status IN ('completed', 'finished')"
        else:
            where = "payment_status IN ('failed', 'expired', 'error', 'timeout')"
            
        return await conn.fetchval(f'SELECT COUNT(*) FROM payments WHERE {where}')

async def get_order(pool, transaction_id: str):
    async with pool.acquire() as conn:
        return await conn.fetchrow('SELECT * FROM payments WHERE transaction_id = $1', transaction_id)

async def get_admin_order_stats(pool):
    async with pool.acquire() as conn:
        records = await conn.fetch('''
            SELECT 
                CASE 
                    WHEN payment_status IN ('completed', 'finished') THEN 'completed'
                    WHEN payment_status IN ('pending', 'waiting', 'confirming', 'sending') THEN 'pending'
                    ELSE 'failed'
                END as category,
                COUNT(*) as count,
                SUM(COALESCE(amount, 0)) as total_amount
            FROM payments
            GROUP BY CASE 
                    WHEN payment_status IN ('completed', 'finished') THEN 'completed'
                    WHEN payment_status IN ('pending', 'waiting', 'confirming', 'sending') THEN 'pending'
                    ELSE 'failed'
                END
        ''')
        
        stats = {
            'completed': {'count': 0, 'amount': 0.0},
            'pending': {'count': 0, 'amount': 0.0},
            'failed': {'count': 0, 'amount': 0.0}
        }
        
        for r in records:
            cat = r['category']
            stats[cat]['count'] = r['count']
            stats[cat]['amount'] = float(r['total_amount'])
            
        return stats