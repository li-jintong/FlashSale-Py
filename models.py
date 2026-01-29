from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)

class Goods(Base):
    __tablename__ = "goods"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    stock = Column(Integer)  # 总库存

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    goods_id = Column(Integer, ForeignKey("goods.id"))
    # 状态：0-排队中, 1-成功, 2-失败
    status = Column(Integer, default=0) 
    created_at = Column(DateTime, default=datetime.utcnow)