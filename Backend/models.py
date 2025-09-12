# models.py
from sqlalchemy import String, Integer, ForeignKey,Column,Float, DateTime, Numeric, UniqueConstraint, Boolean
from sqlalchemy.orm import  Mapped, mapped_column, relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("Item", back_populates="owner")  # link to items
    
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))  # VARCHAR requires length!
    price = Column(Float)
    owner_id = Column(Integer, ForeignKey("users.id"))  # link to user
    owner = relationship("User", back_populates="items")
    created_at = Column(DateTime, default=datetime.utcnow)


'''
class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(ForeignKey("groups.id", ondelete="CASCADE"), index=True)
    payer_id = Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    description = Column(String(100))
    amount = Column(Numeric(12, 2))
    currency = Column(String(100)) 
    created_at = Column(DateTime, default=datetime.utcnow)

 group =  relationship(back_populates="expenses")
    splits = relationship(back_populates="expense", cascade="all, delete-orphan")

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    currency = Column(String(10), default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)

    memberships = relationship(back_populates="group", cascade="all, delete-orphan")
    expenses = relationship(back_populates="group", cascade="all, delete-orphan")
'''
