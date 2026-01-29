from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from redis import asyncio as aioredis

# --- MySQL 配置 ---
# 请确保端口是 3307 (因为你之前改了端口)
SQLALCHEMY_DATABASE_URL = "mysql+aiomysql://root:password123@127.0.0.1:3307/flash_sale"

# 1. 必须要定义 engine 变量，main.py 才能找到它
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

# 2. 必须要定义 get_db 变量，Depends(database.get_db) 才能找到它
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# --- Redis 配置 ---
REDIS_URL = "redis://127.0.0.1:6380/0"
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)

async def get_redis():
    return redis_client

