async def get_advanced_db_stats(pool):
    async with pool.acquire() as conn:
        users_count = await conn.fetchval('SELECT COUNT(*) FROM users')
        payments_count = await conn.fetchval('SELECT COUNT(*) FROM payments')
        tickets_count = await conn.fetchval("SELECT COUNT(*) FROM support_tickets WHERE status = 'unsolved'")
        
        connections = await conn.fetchval('''
            SELECT count(*) 
            FROM pg_stat_activity 
            WHERE datname = current_database()
        ''')
        
        db_size = await conn.fetchval('''
            SELECT pg_size_pretty(pg_database_size(current_database()))
        ''')
        
        return {
            'total_users': users_count,
            'total_payments': payments_count,
            'pending_tickets': tickets_count,
            'active_connections': connections,
            'db_size': db_size
        }