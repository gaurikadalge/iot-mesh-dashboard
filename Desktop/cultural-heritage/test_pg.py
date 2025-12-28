import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def test_pg():
    try:
        engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/cultural_heritage", echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(lambda conn: None)
        print("✅ PostgreSQL connection successful!")
    except Exception as e:
        print("❌ PostgreSQL connection failed:", e)

asyncio.run(test_pg())
