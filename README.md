# FlashSale-Py: 高并发秒杀系统实战架构 🚀

这是一个基于分布式架构设计的秒杀系统，旨在解决电商抢购场景下的高并发、数据一致性及系统稳定性问题。

## 🏗️ 架构演进
- **Phase 1**: 基础 FastAPI + MySQL 实现核心下单逻辑。
- **Phase 2**: 引入 **Redis** 内存缓存，使用 **Lua 脚本** 实现原子性预扣库存，保护后端数据库。
- **Phase 3**: 集成 **RabbitMQ** 消息队列，实现异步下单与流量削峰，确保系统在瞬时高并发下的可用性。
- **Phase 4**: 使用 **Locust** 进行压力测试，模拟 1000+ RPS，识别并分析了 Windows 句柄限制及数据库行锁竞争瓶颈。

## 🛠️ 技术栈
- **Web 框架**: FastAPI (Asynchronous)
- **数据库**: MySQL 8.0 (Order persistence)
- **缓存**: Redis (Stock pre-deduction)
- **消息中间件**: RabbitMQ (Async Task Queue)
- **环境编排**: Docker Compose
- **压测工具**: Locust

## 📈 压测复盘
在本地环境进行 1000+ 用户并发测试，实测单机 RPS 达到 **400+**。针对高并发下的 **MySQL Deadlock (1213)** 错误进行了深入分析，并验证了异步解耦架构对后端服务的保护作用。

## 🚀 快速启动
1. 启动容器：`docker-compose up -d`
2. 安装依赖：`pip install -r requirements.txt`
3. 启动应用：`uvicorn main:app --reload`
4. 启动消费者：`python consumer.py`
