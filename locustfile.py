from locust import HttpUser, task, between
import random

class FlashSaleUser(HttpUser):
    # 每个虚拟用户执行完任务后，等待 0.1 到 0.5 秒再执行下一个
    wait_time = between(0.1, 0.5)

    @task
    def buy_goods(self):
        # 模拟不同的用户 ID（这里简单模拟 1 到 1000 号用户）
        user_id = random.randint(1, 1000)
        goods_id = 1
        
        # 压测我们最强的那个接口：RabbitMQ 异步抢购
        self.client.post(f"/order/mq?user_id={user_id}&goods_id={goods_id}")