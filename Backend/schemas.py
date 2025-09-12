from pydantic import BaseModel
from datetime import datetime

# User
class UserCreate(BaseModel):
    name: str
    username: str
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    username: str
    email: str
    created_at: datetime 
    class Config:
        from_attributes = True

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

# Item
class ItemBase(BaseModel):
    name: str
    price: float

class ItemCreate(BaseModel):
    name: str
    price: float
    

class ItemOut(BaseModel):
    id: int
    name: str
    price: float
    owner_name: str
    created_at: datetime 
    class Config:
        from_attributes = True