import asyncio
import json
import aio_pika
from sqlalchemy import update
import database, models

async def process_message(message: aio_pika.IncomingMessage):
    # 使用 manual_ack=False 或者这里手动 handle
    async with message.process():
        data = json.loads(message.body)
        user_id = data["user_id"]
        goods_id = data["goods_id"]
        print(f" [x] 收到订单消息: 用户{user_id} 抢购商品{goods_id}")

        # 异步写入 MySQL
        async with database.AsyncSessionLocal() as db:
            try:
                # 1. 创建订单
                new_order = models.Order(user_id=user_id, goods_id=goods_id, status=1)
                db.add(new_order)
                
                # 2. 扣减数据库库存（最终一致性）
                await db.execute(
                    update(models.Goods)
                    .where(models.Goods.id == goods_id)
                    .values(stock=models.Goods.stock - 1)
                )
                
                await db.commit()
                print(f" [OK] 数据库写入成功！")
            except Exception as e:
                print(f" [Error] 写入失败: {e}")
                await db.rollback()

async def main():
    # 连接 RabbitMQ
    connection = await aio_pika.connect("amqp://guest:guest@127.0.0.1:5672/")
    channel = await connection.channel()
    
    # 确保队列存在
    queue = await channel.declare_queue("order_queue", durable=True)
    
    print(' [*] 消费者已启动，监听中... 按 CTRL+C 退出')
    
    # 开始消费
    await queue.consume(process_message)

    try:
        # 保持程序不退出
        await asyncio.Future()
    finally:
        await connection.close()

if __name__ == "__main__":
    asyncio.run(main())