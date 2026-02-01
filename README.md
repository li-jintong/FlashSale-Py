# FlashSale-Py: High-Concurrency Flash Sale Architecture 🚀

A high-performance flash sale system built on a distributed architecture, designed to handle extreme traffic spikes, ensure data consistency, and maintain system stability during e-commerce "lightning sale" scenarios.

## 🏗️ Architectural Evolution
- **Phase 1**: Basic MVP – Implemented core ordering logic using FastAPI and MySQL.
- **Phase 2**: Cache Layer Integration – Introduced Redis for in-memory stock management. Leveraged Lua Scripts for atomic stock pre-deduction to prevent overselling and protect the database.
- **Phase 3**: Asynchronous Decoupling – Integrated RabbitMQ for message queuing. Implemented asynchronous order processing and "load shifting" (throttling) to ensure system availability during instantaneous traffic bursts.
- **Phase 4**: Load Testing & Optimization – Utilized Locust to simulate 1000+ RPS. Identified and resolved bottlenecks including Windows file descriptor limits and MySQL row-level lock contention.

## 🛠️ Tech Stack
- **Web Framework**: FastAPI (Asynchronous)
- **Database**: MySQL 8.0 (Order persistence)
- **Caching**: Redis (Stock pre-deduction)
- **Message Broker**: RabbitMQ (Async Task Queue)
- **Orchestration**: Docker Compose
- **Load Testing**: Locust

## 📈 Load Testing Insights
Conducted concurrency tests with 1000+ virtual users, achieving a standalone throughput of 400+ RPS (Requests Per Second).

## 🚀 快速启动
1. Spin up Infrastructure：`docker-compose up -d`
2. Install Dependencies：`pip install -r requirements.txt`
3. Launch Application：`uvicorn main:app --reload`
4. Start Worker：`python consumer.py`
