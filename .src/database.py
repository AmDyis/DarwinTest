import asyncpg
import asyncio

async def get_connection():
    return await asyncpg.connect(database='testTodo', user='postgres', password='4545', host='localhost')

async def create_tables():
    conn = await get_connection()
    async with conn.transaction():
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS Users(
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS Tasks(
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            owner_id INTEGER NOT NULL REFERENCES Users(id)
        )
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS Tasks_Permission(
            id SERIAL PRIMARY KEY,
            task_id INTEGER NOT NULL REFERENCES Tasks(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
            can_read BOOLEAN NOT NULL DEFAULT FALSE,
            can_update BOOLEAN NOT NULL DEFAULT FALSE,
            can_delete BOOLEAN NOT NULL DEFAULT FALSE,
            UNIQUE(task_id, user_id)
        )
        """)
    await conn.close()

if __name__ == "__main__":
    asyncio.run(create_tables())
    print("Done DB")
