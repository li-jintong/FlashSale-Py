# save as seed_users.py
import asyncio
from database import AsyncSessionLocal
from models import User

async def seed():
    async with AsyncSessionLocal() as db:
        print("正在创建 1000 个虚拟用户...")
        for i in range(1, 1001):
            user = User(username=f"user_{i}")
            db.add(user)
        await db.commit()
        print("用户创建完毕！")

if __name__ == "__main__":
    asyncio.run(seed())