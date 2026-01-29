from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy import text
from database import engine, Base, get_db, redis_client  # 加上这个 redis_client
import models
import database
import aio_pika
import json

app = FastAPI()

# 在 main.py 顶部定义
LUA_STOCK_DECR = """
local stock = tonumber(redis.call('get', KEYS[1]))
if (not stock or stock <= 0) then
    return -1
else
    redis.call('decr', KEYS[1])
    return 1
end
"""


@app.post("/order/mq")
async def create_order_mq(user_id: int, goods_id: int):
    # 1. 依然是 Redis 预扣（第一道防线）
    res = await database.redis_client.eval(LUA_STOCK_DECR, 1, f"stock:{goods_id}")
    if res == -1:
        raise HTTPException(status_code=400, detail="已售罄")

    # 2. 将订单信息发送到 RabbitMQ 队列
    connection = await aio_pika.connect("amqp://guest:guest@127.0.0.1:5672/")
    async with connection:
        channel = await connection.channel()
        # 声明持久化队列
        queue = await channel.declare_queue("order_queue", durable=True)
        
        message = {
            "user_id": user_id, 
            "goods_id": goods_id
        }
        
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                #delivery_mode=aio_pika.DeliveryMode.Persistent
                delivery_mode=2
            ),
            routing_key="order_queue",
        )

    # 3. 重点：不需要等待 MySQL，直接返回！
    return {"msg": "抢购成功，订单处理中...", "status": 200}


@app.on_event("startup")
async def startup():
    # 1. 原有的创建表逻辑
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    
    # 2. 库存预热：把商品 1 的库存同步到 Redis
    # 在实际生产中，这里会循环所有在售商品
    async with database.AsyncSessionLocal() as db:
        res = await db.execute(select(models.Goods).where(models.Goods.id == 1))
        goods = res.scalar_one_or_none()
        if goods:
            await database.redis_client.set(f"stock:{goods.id}", goods.stock)
            print(f"库存预热完成：商品{goods.id} 库存={goods.stock}")

@app.post("/init_data")
async def init_data(db: AsyncSession = Depends(database.get_db)):
    # 1. 先清空旧数据（可选，为了干净）
    async with database.engine.begin() as conn:
        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        await conn.execute(text("TRUNCATE TABLE orders;"))
        await conn.execute(text("TRUNCATE TABLE goods;"))
        await conn.execute(text("TRUNCATE TABLE users;"))
        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

    # 2. 创建一个测试用户 ID=1
    user = models.User(id=1, username="test_user")
    # 3. 创建一个测试商品 ID=1
    item = models.Goods(id=1, title="iPhone 15", stock=10)
    
    db.add(user)
    db.add(item)
    await db.commit()
    return {"msg": "初始化成功：用户ID=1, 商品ID=1, 库存10"}

@app.post("/order/simple")
async def create_order(user_id: int, goods_id: int, db: AsyncSession = Depends(database.get_db)):
    # 悲观锁事务
    async with db.begin():
        res = await db.execute(select(models.Goods).where(models.Goods.id == goods_id).with_for_update())
        goods = res.scalar_one_or_none()
        
        if not goods or goods.stock <= 0:
            raise HTTPException(status_code=400, detail="没货了")
            
        goods.stock -= 1
        order = models.Order(user_id=user_id, goods_id=goods_id)
        db.add(order)
    return {"msg": "抢购成功"}



@app.post("/order/redis")
async def create_order_redis(user_id: int, goods_id: int, db: AsyncSession = Depends(database.get_db)):

    print(f"正在为用户 {user_id} 抢购商品 {goods_id}")
    # 1. 核心：在 Redis 中预扣库存
    # eval 保证了这两行逻辑在 Redis 内部是绝对原子的
    # 在 main.py 顶部定义
    res = await database.redis_client.eval(LUA_STOCK_DECR, 1, f"stock:{goods_id}")
    print(f"Redis Lua 返回值: {res}")

    if res == -1:
        raise HTTPException(status_code=400, detail="商品已售罄（Redis拦截）")
    
    # 2. Redis 扣减成功后，再去异步写数据库
    # 注意：此时我们还没用消息队列，先直接写库，下个阶段再引入 RabbitMQ
    try:
        new_order = models.Order(user_id=user_id, goods_id=goods_id, status=1)
        db.add(new_order)
        # 别忘了更新数据库里的库存，保持最终一致性
        await db.execute(
            update(models.Goods).where(models.Goods.id == goods_id).values(stock=models.Goods.stock - 1)
        )
        await db.commit()
    except Exception as e:
        # 如果数据库写失败了，记得把 Redis 的库存补回去（回滚）
        await redis_client.incr(f"stock:{goods_id}")
        raise HTTPException(status_code=500, detail="系统繁忙，下单失败")

    return {"msg": "抢购成功（Redis扣减）"}