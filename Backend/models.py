# models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(200))
    items = relationship("Item", back_populates="owner")  # link to items

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))  # VARCHAR requires length!
    price = Column(Float)
    owner_id = Column(Integer, ForeignKey("users.id"))  # link to user
    owner = relationship("User", back_populates="items")
